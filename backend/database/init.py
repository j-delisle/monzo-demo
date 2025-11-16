import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.config import SessionLocal, create_tables, engine
from database.models import User, Account, Transaction, TopUpRule, TopUpEvent
from auth.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

def is_database_empty() -> bool:
    """Check if database is empty (no users)"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        return user_count == 0
    finally:
        db.close()

def seed_demo_data():
    """Seed database with demo data"""
    db = SessionLocal()
    try:
        logger.info("Seeding database with demo data...")
        
        # Create demo users
        demo_user = User(
            id="user_1",
            email="demo@monzo.com",
            name="Demo User",
            password_hash=get_password_hash("demo"),
            created_at=datetime.now()
        )
        
        john_user = User(
            id="user_2",
            email="john@example.com", 
            name="John Doe",
            password_hash=get_password_hash("demo"),
            created_at=datetime.now()
        )
        
        db.add(demo_user)
        db.add(john_user)
        db.commit()
        
        # Create demo accounts
        demo_current = Account(
            id="acc_1",
            name="Current Account", 
            balance=150.50,
            user_id="user_1"
        )
        
        demo_savings = Account(
            id="acc_2",
            name="Savings Account",
            balance=1250.00,
            user_id="user_1"
        )
        
        john_current = Account(
            id="acc_3",
            name="Current Account",
            balance=89.23,
            user_id="user_2"
        )
        
        db.add(demo_current)
        db.add(demo_savings)
        db.add(john_current)
        db.commit()
        
        # Create sample transactions
        sample_transactions = [
            Transaction(
                id=str(uuid.uuid4()),
                account_id="acc_1",
                amount=25.50,
                merchant="Tesco",
                description="Weekly groceries",
                category="Shopping",
                transaction_type="debit",
                timestamp=datetime.now() - timedelta(days=2)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                account_id="acc_1",
                amount=12.30,
                merchant="Costa Coffee",
                description="Morning coffee",
                category="Food & Drink",
                transaction_type="debit",
                timestamp=datetime.now() - timedelta(days=1)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                account_id="acc_1",
                amount=500.00,
                merchant="Salary",
                description="Monthly salary",
                category="Income",
                transaction_type="credit",
                timestamp=datetime.now() - timedelta(days=5)
            ),
            Transaction(
                id=str(uuid.uuid4()),
                account_id="acc_2",
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
        
        # Create sample topup rules
        topup_rule = TopUpRule(
            id=str(uuid.uuid4()),
            account_id="acc_1",
            threshold=50.0,
            topup_amount=100.0,
            enabled=True
        )
        
        db.add(topup_rule)
        
        # Create sample topup event
        topup_event = TopUpEvent(
            id=str(uuid.uuid4()),
            account_id="acc_1",
            amount=100.0,
            triggered_balance=25.50,
            timestamp=datetime.now() - timedelta(days=3)
        )
        
        db.add(topup_event)
        
        db.commit()
        logger.info("Demo data seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize database with tables and demo data"""
    try:
        logger.info("Initializing database...")
        
        # Create tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Seed data if database is empty
        if is_database_empty():
            logger.info("Database is empty, seeding with demo data...")
            seed_demo_data()
        else:
            logger.info("Database already contains data, skipping seeding")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise