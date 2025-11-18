import uuid
import subprocess
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.config import SessionLocal, engine
from database.models import User, Account, Transaction, TopUpRule, TopUpEvent
from auth.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations to ensure database is up to date"""
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Database migrations completed successfully")
        logger.debug(f"Migration output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise

def init_database():
    """Initialize database with migrations only"""
    try:
        logger.info("Initializing database...")
        
        # Run migrations to create/update tables
        run_migrations()
        logger.info("Database tables created/updated via migrations")
        logger.info("Database initialization completed - run 'python seed_database.py' to add demo data")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise