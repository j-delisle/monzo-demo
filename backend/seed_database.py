#!/usr/bin/env python3
"""Script to seed the database with demo data"""

import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from database.config import SessionLocal
from database.models import User, Account, Transaction, TopUpRule, TopUpEvent
from auth.auth import get_password_hash
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo_data():
    """Seed database with demo data"""
    db = SessionLocal()
    try:
        logger.info("Seeding database with demo data...")
        
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.email == "demo@monzo.com").first()
        if existing_user:
            logger.info("Demo data already exists, skipping seeding")
            return
        
        # Create demo users (IDs will be auto-generated)
        demo_user = User(
            email="demo@monzo.com",
            name="Demo User",
            password_hash=get_password_hash("demo"),
            created_at=datetime.now()
        )
        
        john_user = User(
            email="john@example.com", 
            name="John Doe",
            password_hash=get_password_hash("demo"),
            created_at=datetime.now()
        )
        
        db.add(demo_user)
        db.add(john_user)
        db.commit()
        
        # Create demo accounts (use the generated user IDs)
        demo_current = Account(
            name="Current Account", 
            balance=150.50,
            user_id=demo_user.id
        )
        
        demo_savings = Account(
            name="Savings Account",
            balance=1250.00,
            user_id=demo_user.id
        )
        
        john_current = Account(
            name="Current Account",
            balance=89.23,
            user_id=john_user.id
        )
        
        db.add(demo_current)
        db.add(demo_savings)
        db.add(john_current)
        db.commit()
        
        # Create sample transactions (use generated account IDs)
        sample_transactions = [
            Transaction(
                account_id=demo_current.id,
                amount=25.50,
                merchant="Tesco",
                description="Weekly groceries",
                category="Shopping",
                transaction_type="debit",
                timestamp=datetime.now() - timedelta(days=2)
            ),
            Transaction(
                account_id=demo_current.id,
                amount=12.30,
                merchant="Costa Coffee",
                description="Morning coffee",
                category="Food & Drink",
                transaction_type="debit",
                timestamp=datetime.now() - timedelta(days=1)
            ),
            Transaction(
                account_id=demo_current.id,
                amount=500.00,
                merchant="Salary",
                description="Monthly salary",
                category="Income",
                transaction_type="credit",
                timestamp=datetime.now() - timedelta(days=5)
            ),
            Transaction(
                account_id=demo_savings.id,
                amount=100.00,
                merchant="Transfer",
                description="Monthly savings",
                category="Transfer",
                transaction_type="credit",
                timestamp=datetime.now() - timedelta(days=1)
            )
        ]
        
        for transaction in sample_transactions:
            db.add(transaction)
        
        # Create sample topup rules (use generated account IDs)
        topup_rule = TopUpRule(
            account_id=demo_current.id,
            threshold=50.0,
            topup_amount=100.0,
            enabled=True
        )
        
        db.add(topup_rule)
        
        # Create sample topup event (use generated account IDs)
        topup_event = TopUpEvent(
            account_id=demo_current.id,
            amount=100.0,
            triggered_balance=25.50,
            timestamp=datetime.now() - timedelta(days=3)
        )
        
        db.add(topup_event)
        
        db.commit()
        logger.info("✅ Demo data seeded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()