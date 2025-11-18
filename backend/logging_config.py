import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "monzo-api",
            "version": "1.0.0"
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'account_id'):
            log_entry["account_id"] = record.account_id
        if hasattr(record, 'transaction_id'):
            log_entry["transaction_id"] = record.transaction_id
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, 'error_type'):
            log_entry["error_type"] = record.error_type
        if hasattr(record, 'category'):
            log_entry["category"] = record.category
        if hasattr(record, 'amount'):
            log_entry["amount"] = record.amount
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add stack trace for errors
        if record.levelno >= logging.ERROR and record.stack_info:
            log_entry["stack_trace"] = record.stack_info
            
        return json.dumps(log_entry)

def setup_logging():
    """Set up structured logging configuration"""
    
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    api_logger = logging.getLogger("monzo.api")
    api_logger.setLevel(logging.INFO)
    
    auth_logger = logging.getLogger("monzo.auth")
    auth_logger.setLevel(logging.INFO)
    
    db_logger = logging.getLogger("monzo.database")
    db_logger.setLevel(logging.INFO)
    
    metrics_logger = logging.getLogger("monzo.metrics")
    metrics_logger.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured logging configured"""
    return logging.getLogger(f"monzo.{name}")

# Convenience functions for structured logging
def log_transaction_created(logger: logging.Logger, user_id: str, account_id: str, 
                          transaction_id: str, amount: float, category: str, merchant: str):
    """Log transaction creation event"""
    logger.info(
        "Transaction created successfully",
        extra={
            "user_id": user_id,
            "account_id": account_id,
            "transaction_id": transaction_id,
            "amount": amount,
            "category": category,
            "merchant": merchant,
            "event_type": "transaction_created"
        }
    )

def log_topup_triggered(logger: logging.Logger, user_id: str, account_id: str, 
                       amount: float, triggered_balance: float, rule_id: str):
    """Log topup trigger event"""
    logger.info(
        "TopUp triggered successfully",
        extra={
            "user_id": user_id,
            "account_id": account_id,
            "amount": amount,
            "triggered_balance": triggered_balance,
            "rule_id": rule_id,
            "event_type": "topup_triggered"
        }
    )

def log_categorizer_request(logger: logging.Logger, merchant: str, amount: float, 
                          category: str, duration_ms: float, success: bool):
    """Log categorizer service request"""
    level = logging.INFO if success else logging.WARNING
    message = "Categorizer request completed" if success else "Categorizer request failed"
    
    logger.log(
        level,
        message,
        extra={
            "merchant": merchant,
            "amount": amount,
            "category": category,
            "duration_ms": duration_ms,
            "success": success,
            "event_type": "categorizer_request"
        }
    )

def log_auth_attempt(logger: logging.Logger, auth_type: str, email: str, 
                    success: bool, error_type: str = None):
    """Log authentication attempt"""
    level = logging.INFO if success else logging.WARNING
    message = f"{auth_type} attempt {'successful' if success else 'failed'}"
    
    extra_data = {
        "auth_type": auth_type,
        "email": email,
        "success": success,
        "event_type": "auth_attempt"
    }
    
    if not success and error_type:
        extra_data["error_type"] = error_type
    
    logger.log(level, message, extra=extra_data)

def log_api_request(logger: logging.Logger, method: str, endpoint: str, 
                   status_code: int, duration_ms: float, user_id: str = None):
    """Log API request"""
    level = logging.INFO if status_code < 400 else logging.WARNING
    
    extra_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "event_type": "api_request"
    }
    
    if user_id:
        extra_data["user_id"] = user_id
    
    logger.log(
        level,
        f"{method} {endpoint} - {status_code}",
        extra=extra_data
    )

def log_database_error(logger: logging.Logger, operation: str, table: str, 
                      error: Exception, user_id: str = None):
    """Log database error"""
    extra_data = {
        "operation": operation,
        "table": table,
        "error_type": type(error).__name__,
        "event_type": "database_error"
    }
    
    if user_id:
        extra_data["user_id"] = user_id
    
    logger.error(
        f"Database {operation} failed on {table}: {str(error)}",
        extra=extra_data,
        exc_info=True
    )