from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import *
from database import db
from auth.routes import router as auth_router
from auth.auth import get_current_user
import httpx
import uuid
from datetime import datetime
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Monzo Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router)

CATEGORIZER_URL = "http://categorizer:9000"

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path} from {request.client.host}")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/")
async def root():
    return {"message": "Monzo Demo API"}

@app.get("/accounts", response_model=List[Account])
async def get_accounts(current_user: User = Depends(get_current_user)):
    return db.get_accounts_by_user(current_user.id)

@app.get("/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.get("/transactions", response_model=List[Transaction])
async def get_transactions(account_id: str = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_transactions = db.get_transactions(account_id)
    return [t for t in all_transactions if t.account_id in user_account_ids]

@app.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: CreateTransaction, current_user: User = Depends(get_current_user)):
    logger.info(f"Creating transaction: {transaction_data}")
    account = db.get_account_by_user(transaction_data.account_id, current_user.id)
    if not account:
        logger.error(f"Account not found: {transaction_data.account_id}")
        raise HTTPException(status_code=404, detail="Account not found")
    logger.info(f"Found account: {account}")

    # Get category from Go microservice
    category = "Other"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CATEGORIZER_URL}/categorize",
                json={
                    "merchant": transaction_data.merchant,
                    "amount": transaction_data.amount,
                    "description": transaction_data.description
                },
                timeout=5.0
            )
            if response.status_code == 200:
                category = response.json().get("category", "Other")
    except Exception as e:
        print(f"Failed to categorize transaction: {e}")

    # Create transaction
    transaction = Transaction(
        id=str(uuid.uuid4()),
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

    db.update_account_balance(transaction_data.account_id, new_balance)
    db.add_transaction(transaction)

    # Check for auto topup
    await check_and_trigger_topup(transaction_data.account_id)

    logger.info(f"Transaction created successfully: {transaction}")
    return transaction

@app.get("/topup-rules", response_model=List[TopUpRule])
async def get_topup_rules(account_id: str = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_rules = db.get_topup_rules(account_id)
    return [r for r in all_rules if r.account_id in user_account_ids]

@app.post("/topup-rules", response_model=TopUpRule)
async def create_topup_rule(rule_data: CreateTopUpRule, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(rule_data.account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    rule = TopUpRule(
        id=str(uuid.uuid4()),
        account_id=rule_data.account_id,
        threshold=rule_data.threshold,
        topup_amount=rule_data.topup_amount,
        enabled=True
    )

    return db.add_topup_rule(rule)

@app.get("/topup-events", response_model=List[TopUpEvent])
async def get_topup_events(account_id: str = None, current_user: User = Depends(get_current_user)):
    if account_id:
        account = db.get_account_by_user(account_id, current_user.id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
    user_accounts = db.get_accounts_by_user(current_user.id)
    user_account_ids = [acc.id for acc in user_accounts]
    all_events = db.get_topup_events(account_id)
    return [e for e in all_events if e.account_id in user_account_ids]

@app.post("/trigger-topup")
async def manual_trigger_topup(account_id: str, current_user: User = Depends(get_current_user)):
    account = db.get_account_by_user(account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    result = await check_and_trigger_topup(account_id)
    return {"triggered": result["triggered"], "message": result["message"]}

async def check_and_trigger_topup(account_id: str):
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

            # Log topup event
            event = TopUpEvent(
                id=str(uuid.uuid4()),
                account_id=account_id,
                amount=rule.topup_amount,
                triggered_balance=account.balance,
                timestamp=datetime.now()
            )
            db.add_topup_event(event)

            return {
                "triggered": True,
                "message": f"TopUp of £{rule.topup_amount} triggered. New balance: £{new_balance}"
            }

    return {"triggered": False, "message": "No topup rules triggered"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
