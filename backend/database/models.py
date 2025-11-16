from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    topup_rules = relationship("TopUpRule", back_populates="account", cascade="all, delete-orphan")
    topup_events = relationship("TopUpEvent", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    transaction_type = Column(String, nullable=False)  # "debit" or "credit"
    timestamp = Column(DateTime, default=datetime.now)
    
    account = relationship("Account", back_populates="transactions")

class TopUpRule(Base):
    __tablename__ = "topup_rules"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    threshold = Column(Float, nullable=False)
    topup_amount = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True)
    
    account = relationship("Account", back_populates="topup_rules")

class TopUpEvent(Base):
    __tablename__ = "topup_events"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    triggered_balance = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    account = relationship("Account", back_populates="topup_events")