from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import time
from typing import Dict, Any
from contextlib import contextmanager

# Create a registry for our metrics
registry = CollectorRegistry()

# Transaction metrics
transactions_total = Counter(
    'transactions_total',
    'Total number of transactions created',
    ['transaction_type', 'account_id', 'category'],
    registry=registry
)

# TopUp metrics
topups_triggered_total = Counter(
    'topups_triggered_total',
    'Total number of topups triggered',
    ['account_id'],
    registry=registry
)

# API request metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Categorizer metrics
categorizer_requests_total = Counter(
    'categorizer_requests_total',
    'Total number of requests to categorizer service',
    ['status'],
    registry=registry
)

categorizer_failures_total = Counter(
    'categorizer_failures_total',
    'Total number of categorizer service failures',
    registry=registry
)

categorizer_latency_seconds = Histogram(
    'categorizer_latency_seconds',
    'Categorizer service response time in seconds',
    registry=registry
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total number of authentication attempts',
    ['type', 'status'],  # type: login/signup/demo, status: success/failure
    registry=registry
)

# Database metrics
database_operations_total = Counter(
    'database_operations_total',
    'Total number of database operations',
    ['operation', 'table', 'status'],
    registry=registry
)

database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=registry
)

# Account metrics
accounts_total = Gauge(
    'accounts_total',
    'Total number of accounts in system',
    registry=registry
)

account_balance_total = Gauge(
    'account_balance_total',
    'Total balance across all accounts',
    registry=registry
)

@contextmanager
def track_request_duration(method: str, endpoint: str):
    """Context manager to track request duration"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        api_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

@contextmanager
def track_categorizer_duration():
    """Context manager to track categorizer service duration"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        categorizer_latency_seconds.observe(duration)

def get_metrics() -> str:
    """Get all metrics in Prometheus format"""
    return generate_latest(registry)

def record_transaction(transaction_type: str, account_id: str, category: str):
    """Record a transaction creation"""
    transactions_total.labels(
        transaction_type=transaction_type,
        account_id=account_id,
        category=category
    ).inc()

def record_topup(account_id: str):
    """Record a topup trigger"""
    topups_triggered_total.labels(account_id=account_id).inc()

def record_api_request(method: str, endpoint: str, status_code: int):
    """Record an API request"""
    api_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()

def record_categorizer_request(status: str):
    """Record a categorizer service request"""
    categorizer_requests_total.labels(status=status).inc()

def record_categorizer_failure():
    """Record a categorizer service failure"""
    categorizer_failures_total.inc()

def record_auth_attempt(auth_type: str, status: str):
    """Record an authentication attempt"""
    auth_attempts_total.labels(type=auth_type, status=status).inc()

def record_database_operation(operation: str, table: str, status: str):
    """Record a database operation"""
    database_operations_total.labels(
        operation=operation,
        table=table,
        status=status
    ).inc()

def update_accounts_count(count: int):
    """Update total accounts gauge"""
    accounts_total.set(count)

def update_total_balance(balance: float):
    """Update total balance gauge"""
    account_balance_total.set(balance)

def update_active_connections(count: int):
    """Update active database connections"""
    database_connections_active.set(count)