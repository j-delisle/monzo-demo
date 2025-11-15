from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Account(BaseModel):
    id: str
    name: str
    balance: float
    user_id: str

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class Transaction(BaseModel):
    id: str
    account_id: str
    amount: float
    merchant: str
    description: str
    category: Optional[str] = None
    transaction_type: TransactionType
    timestamp: datetime

class CreateTransaction(BaseModel):
    account_id: str
    amount: float
    merchant: str
    description: str
    transaction_type: TransactionType

class TopUpRule(BaseModel):
    id: str
    account_id: str
    threshold: float
    topup_amount: float
    enabled: bool = True

class CreateTopUpRule(BaseModel):
    account_id: str
    threshold: float
    topup_amount: float

class TopUpEvent(BaseModel):
    id: str
    account_id: str
    amount: float
    triggered_balance: float
    timestamp: datetime

class CategorizationRequest(BaseModel):
    merchant: str
    amount: float
    description: str

class CategorizationResponse(BaseModel):
    category: str