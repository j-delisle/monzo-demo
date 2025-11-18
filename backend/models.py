from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

class Account(BaseModel):
    id: int
    uuid: str  # UUID as string for JSON serialization
    name: str
    balance: float
    user_id: int

class CreateAccount(BaseModel):
    name: str
    balance: float
    user_id: int

class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class Transaction(BaseModel):
    id: int
    account_id: int
    amount: float
    merchant: str
    description: str
    category: Optional[str] = None
    transaction_type: TransactionType
    timestamp: datetime

class CreateTransaction(BaseModel):
    account_id: int
    amount: float
    merchant: str
    description: str
    transaction_type: TransactionType

class TopUpRule(BaseModel):
    id: int
    account_id: int
    threshold: float
    topup_amount: float
    enabled: bool = True

class CreateTopUpRule(BaseModel):
    account_id: int
    threshold: float
    topup_amount: float

class TopUpEvent(BaseModel):
    id: int
    account_id: int
    amount: float
    triggered_balance: float
    timestamp: datetime

class CategorizationRequest(BaseModel):
    merchant: str
    amount: float
    description: str

class CategorizationResponse(BaseModel):
    category: str

# Auth Models
class User(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
