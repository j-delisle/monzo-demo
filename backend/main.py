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

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Update system-wide metrics before serving
    accounts = db.get_accounts()
    update_accounts_count(len(accounts))
    total_balance = sum(acc.balance for acc in accounts)
    update_total_balance(total_balance)

    return Response(content=get_metrics(), media_type="text/plain")

# JSON metrics endpoint for frontend
@app.get("/api/metrics")
async def api_metrics():
    """JSON metrics endpoint for frontend dashboard"""
    try:
        # Update system-wide metrics
        accounts = db.get_accounts()
        update_accounts_count(len(accounts))
        total_balance = sum(acc.balance for acc in accounts)
        update_total_balance(total_balance)

        # Get our own metrics
        backend_metrics = get_metrics()

        # Fetch Go categorizer metrics
        categorizer_metrics = ""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{CATEGORIZER_URL}/metrics", timeout=5.0)
                if response.status_code == 200:
                    categorizer_metrics = response.text
        except Exception as e:
            logger.warning(f"Failed to fetch categorizer metrics: {str(e)}")

        # Parse metrics and return JSON
        parsed_metrics = parse_prometheus_metrics(backend_metrics, categorizer_metrics)
        return parsed_metrics

    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return {"error": "Failed to retrieve metrics"}

# Categories breakdown endpoint
@app.get("/api/metrics/categories")
async def get_categories_breakdown():
    """Get real transaction category breakdown"""
    try:
        transactions = db.get_all_transactions()

        if not transactions:
            return {"categories": []}

        # Count transactions by category
        category_counts = {}
        total_transactions = len(transactions)

        for transaction in transactions:
            category = transaction.category or "Other"
            category_counts[category] = category_counts.get(category, 0) + 1

        # Convert to percentages and format for chart
        categories = []
        colors = {
            'Food & Drink': '#ff6b6b',
            'Transport': '#4ecdc4',
            'Shopping': '#45b7d1',
            'Groceries': '#96ceb4',
            'Entertainment': '#ffeaa7',
            'Bills & Utilities': '#dda0dd',
            'Housing': '#fab1a0',
            'Income': '#00b894',
            'ATM': '#a29bfe',
            'Other': '#6c5ce7'
        }

        for category, count in category_counts.items():
            percentage = round((count / total_transactions) * 100, 1)
            categories.append({
                "name": category,
                "value": percentage,
                "count": count,
                "color": colors.get(category, '#6c5ce7')  # Default to Other color
            })

        # Sort by percentage descending
        categories.sort(key=lambda x: x['value'], reverse=True)

        return {"categories": categories, "total_transactions": total_transactions}

    except Exception as e:
        logger.error(f"Failed to get category breakdown: {str(e)}")
        return {"error": "Failed to retrieve category data"}

# Time series endpoint
@app.get("/api/metrics/timeseries")
async def get_timeseries_data():
    """Get time series data for charts - currently simulated from real metrics"""
    try:
        # Get current real metrics
        accounts = db.get_accounts()
        transactions = db.get_all_transactions()

        # Get recent transaction timestamps for realistic distribution
        recent_transactions = [t for t in transactions
                             if (datetime.now() - t.timestamp).days < 1]

        # Generate realistic hourly data based on actual transaction patterns
        time_series = []
        current_hour = datetime.now().hour

        for i in range(24):
            hour_index = (current_hour - 23 + i) % 24
            hour = hour_index if hour_index >= 0 else hour_index + 24

            # Count actual transactions in this hour from recent data
            hour_transactions = [t for t in recent_transactions
                               if t.timestamp.hour == hour]

            actual_count = len(hour_transactions)

            # Use real data when available, simulate realistic patterns when not
            if actual_count > 0:
                transactions_count = actual_count
                categorizer_requests = actual_count  # 1:1 ratio
                errors = 0  # Assume success for real data
            else:
                # Simulate realistic patterns: higher during business hours
                if 9 <= hour <= 17:  # Business hours
                    base_transactions = 15
                elif 18 <= hour <= 22:  # Evening
                    base_transactions = 8
                elif 6 <= hour <= 8:  # Morning
                    base_transactions = 5
                else:  # Night
                    base_transactions = 1

                transactions_count = max(0, base_transactions + (i % 3) - 1)
                categorizer_requests = transactions_count
                errors = 1 if transactions_count > 10 and (i % 7) == 0 else 0

            # Real-ish response time simulation (based on load)
            if transactions_count > 10:
                response_time = 120 + (transactions_count * 2)  # Higher load = slower
            else:
                response_time = 50 + (transactions_count * 5)

            time_series.append({
                "hour": f"{hour:02d}:00",
                "transactions": transactions_count,
                "categorizer_requests": categorizer_requests,
                "errors": errors,
                "response_time": min(response_time, 500)  # Cap at 500ms
            })

        return {
            "timeseries": time_series,
            "metadata": {
                "total_transactions_today": len(recent_transactions),
                "data_source": "real_data_with_simulation"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get timeseries data: {str(e)}")
        return {"error": "Failed to retrieve timeseries data"}

def parse_prometheus_metrics(backend_metrics: str, categorizer_metrics: str) -> dict:
    """Parse Prometheus format metrics and return structured JSON"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "backend": {},
        "categorizer": {},
        "summary": {}
    }

    # Helper function to extract metric value
    def extract_metric_value(lines: List[str], metric_name: str) -> float:
        for line in lines:
            if line.startswith(metric_name) and not line.startswith(f"{metric_name}_"):
                try:
                    return float(line.split()[-1])
                except (IndexError, ValueError):
                    continue
        return 0.0

    def extract_counter_by_label(lines: List[str], metric_name: str, label_filters: dict = None) -> float:
        total = 0.0
        for line in lines:
            if line.startswith(metric_name) and "{" in line:
                if label_filters:
                    # Check if all label filters match
                    if all(f'{key}="{value}"' in line for key, value in label_filters.items()):
                        try:
                            total += float(line.split()[-1])
                        except (IndexError, ValueError):
                            continue
                else:
                    try:
                        total += float(line.split()[-1])
                    except (IndexError, ValueError):
                        continue
        return total

    # Parse backend metrics
    backend_lines = backend_metrics.strip().split('\n')
    backend_lines = [line for line in backend_lines if not line.startswith('#') and line.strip()]

    metrics["backend"] = {
        "transactions_total": extract_counter_by_label(backend_lines, "transactions_total"),
        "topups_triggered_total": extract_metric_value(backend_lines, "topups_triggered_total"),
        "api_requests_total": extract_counter_by_label(backend_lines, "api_requests_total"),
        "categorizer_requests_success": extract_counter_by_label(backend_lines, "categorizer_requests_total", {"status": "success"}),
        "categorizer_requests_failure": extract_counter_by_label(backend_lines, "categorizer_requests_total", {"status": "failure"}),
        "accounts_count": extract_metric_value(backend_lines, "accounts_total"),
        "total_balance": extract_metric_value(backend_lines, "account_balance_total")
    }

    # Parse categorizer metrics
    if categorizer_metrics:
        categorizer_lines = categorizer_metrics.strip().split('\n')
        categorizer_lines = [line for line in categorizer_lines if not line.startswith('#') and line.strip()]

        metrics["categorizer"] = {
            "categorization_requests_total": extract_counter_by_label(categorizer_lines, "categorization_requests_total"),
            "categorization_errors_total": extract_counter_by_label(categorizer_lines, "categorization_errors_total"),
            "http_requests_total": extract_counter_by_label(categorizer_lines, "http_requests_total"),
        }

    # Calculate summary metrics
    total_categorizer_requests = metrics["categorizer"].get("categorization_requests_total", 0)
    total_categorizer_errors = metrics["categorizer"].get("categorization_errors_total", 0)

    # Get total transaction count from database for accuracy
    try:
        all_transactions = db.get_all_transactions()
        actual_transaction_count = len(all_transactions)
    except:
        actual_transaction_count = metrics["backend"]["transactions_total"]

    metrics["summary"] = {
        "total_transactions": actual_transaction_count,
        "total_accounts": metrics["backend"]["accounts_count"],
        "total_balance": metrics["backend"]["total_balance"],
        "categorizer_success_rate": ((total_categorizer_requests - total_categorizer_errors) / max(total_categorizer_requests, 1)) * 100,
        "categorizer_error_rate": total_categorizer_errors,
        "system_health": "healthy" if total_categorizer_errors < 10 else "degraded"
    }

    return metrics

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
