from fastapi import FastAPI, HTTPException, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from models import (
    CreateTransaction, Transaction as TransactionResponse,
    CreateTopUpRule, TopUpRule as TopUpRuleResponse,
    TopUpEvent as TopUpEventResponse,
    Account as AccountResponse,
    User as UserResponse,
    CategorizationRequest, CategorizationResponse,
    TransactionType
)
from database.models import User, Account, Transaction, TopUpRule, TopUpEvent
from database.repository import db
from database.init import init_database
from auth.routes import router as auth_router
from auth.auth import get_current_user
import httpx
from datetime import datetime
from typing import List
import logging
import time

# Import monitoring modules
from metrics import (
    get_metrics, record_transaction, record_topup, record_api_request,
    record_categorizer_request, record_categorizer_failure, track_request_duration,
    track_categorizer_duration, update_accounts_count, update_total_balance
)
from logging_config import (
    setup_logging, get_logger, log_transaction_created, log_topup_triggered,
    log_categorizer_request, log_api_request
)

# Set up structured logging
setup_logging()
logger = get_logger("api")

app = FastAPI(title="Monzo Demo API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Update system-wide metrics before serving
    accounts = db.get_accounts()
    update_accounts_count(len(accounts))
    total_balance = sum(acc.balance for acc in accounts)
    update_total_balance(total_balance)
    
    return Response(content=get_metrics(), media_type="text/plain")

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    
    # Skip metrics endpoint from tracking to avoid recursion
    if request.url.path == "/metrics":
        return await call_next(request)
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    duration_ms = duration * 1000
    
    # Record metrics
    record_api_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    )
    
    # Log request
    user_id = getattr(request.state, 'user_id', None)
    log_api_request(
        logger=logger,
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        user_id=user_id
    )
    
    return response

# Include auth routes
app.include_router(auth_router)

CATEGORIZER_URL = "http://categorizer:9000"


@app.get("/")
async def root():
    return {"message": "Monzo Demo API"}

@app.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(current_user: User = Depends(get_current_user)):
    return db.get_accounts_by_user(current_user.id)

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(account_id: int = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_transactions = db.get_transactions(account_id)
    return [t for t in all_transactions if t.account_id in user_account_ids]

@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction_data: CreateTransaction, current_user: User = Depends(get_current_user)):
    # Validate account access
    account = db.get_account_by_user(transaction_data.account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Get category from Go microservice with metrics tracking
    category = "Other"
    categorizer_success = False
    
    try:
        with track_categorizer_duration():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CATEGORIZER_URL}/categorize",
                    json={
                        "merchant": transaction_data.merchant,
                        "amount": transaction_data.amount,
                        "description": transaction_data.description,
                        "transaction_type": transaction_data.transaction_type
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    category = response.json().get("category", "Other")
                    categorizer_success = True
                    record_categorizer_request("success")
                else:
                    record_categorizer_request("error")
                    
    except Exception as e:
        record_categorizer_failure()
        record_categorizer_request("failure")
        logger.warning(f"Categorizer service failed: {str(e)}", extra={
            "merchant": transaction_data.merchant,
            "error_type": type(e).__name__,
            "event_type": "categorizer_error"
        })

    # Log categorizer request
    log_categorizer_request(
        logger=logger,
        merchant=transaction_data.merchant,
        amount=transaction_data.amount,
        category=category,
        duration_ms=0,  # Duration tracked separately by context manager
        success=categorizer_success
    )

    # Create transaction
    transaction = Transaction(
        account_id=transaction_data.account_id,
        amount=transaction_data.amount,
        merchant=transaction_data.merchant,
        description=transaction_data.description,
        category=category,
        transaction_type=transaction_data.transaction_type,
        timestamp=datetime.now()
    )

    # Update account balance
    new_balance = account.balance
    if transaction_data.transaction_type == TransactionType.DEBIT:
        new_balance -= transaction_data.amount
    else:
        new_balance += transaction_data.amount

    # Save to database
    db.update_account_balance(transaction_data.account_id, new_balance)
    created_transaction = db.add_transaction(transaction)

    # Record metrics
    record_transaction(
        transaction_type=transaction_data.transaction_type,
        account_id=str(account.id),
        category=category
    )

    # Log transaction creation
    log_transaction_created(
        logger=logger,
        user_id=str(current_user.id),
        account_id=str(account.id),
        transaction_id=str(created_transaction.id),
        amount=transaction_data.amount,
        category=category,
        merchant=transaction_data.merchant
    )

    # Check for auto topup
    await check_and_trigger_topup(transaction_data.account_id)

    return created_transaction

@app.get("/topup-rules", response_model=List[TopUpRuleResponse])
async def get_topup_rules(account_id: int = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_rules = db.get_topup_rules(account_id)
    return [r for r in all_rules if r.account_id in user_account_ids]

@app.post("/topup-rules", response_model=TopUpRuleResponse)
async def create_topup_rule(rule_data: CreateTopUpRule, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(rule_data.account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    rule = TopUpRule(
        account_id=rule_data.account_id,
        threshold=rule_data.threshold,
        topup_amount=rule_data.topup_amount,
        enabled=True
    )

    return db.add_topup_rule(rule)

@app.get("/topup-events", response_model=List[TopUpEventResponse])
async def get_topup_events(account_id: int = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_events = db.get_topup_events(account_id)
    return [e for e in all_events if e.account_id in user_account_ids]

@app.post("/trigger-topup")
async def manual_trigger_topup(account_id: int, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    result = await check_and_trigger_topup(account_id)
    return {"triggered": result["triggered"], "message": result["message"]}

async def check_and_trigger_topup(account_id: int):
    account = db.get_account(account_id)
    if not account:
        return {"triggered": False, "message": "Account not found"}

    rules = db.get_topup_rules(account_id)
    enabled_rules = [r for r in rules if r.enabled]

    for rule in enabled_rules:
        if account.balance < rule.threshold:
            # Trigger topup
            new_balance = account.balance + rule.topup_amount
            db.update_account_balance(account_id, new_balance)

            # Create topup event
            event = TopUpEvent(
                account_id=account_id,
                amount=rule.topup_amount,
                triggered_balance=account.balance,
                timestamp=datetime.now()
            )
            created_event = db.add_topup_event(event)

            # Record metrics
            record_topup(str(account_id))

            # Log topup trigger
            log_topup_triggered(
                logger=logger,
                user_id=str(account.user_id),
                account_id=str(account_id),
                amount=rule.topup_amount,
                triggered_balance=account.balance,
                rule_id=str(rule.id)
            )

            return {
                "triggered": True,
                "message": f"TopUp of ${rule.topup_amount:,.2f} triggered. New balance: ${new_balance:,.2f}"
            }

    return {"triggered": False, "message": "No topup rules triggered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
