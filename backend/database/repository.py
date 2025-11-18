from typing import List, Optional
from sqlalchemy.orm import Session
from database.config import get_database
from database.models import User as DBUser, Account as DBAccount, Transaction as DBTransaction, TopUpRule as DBTopUpRule, TopUpEvent as DBTopUpEvent
from models import User, Account, CreateAccount, Transaction, CreateTransaction, TopUpRule, TopUpEvent

class SQLiteRepository:
    def __init__(self):
        pass

    def _get_db(self) -> Session:
        """Get database session"""
        return next(get_database())

    # User methods
    def get_user_by_email(self, email: str) -> Optional[User]:
        db = self._get_db()
        try:
            db_user = db.query(DBUser).filter(DBUser.email == email).first()
            if db_user:
                return User(
                    id=db_user.id,
                    email=db_user.email,
                    name=db_user.name,
                    created_at=db_user.created_at
                )
            return None
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        db = self._get_db()
        try:
            db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
            if db_user:
                return User(
                    id=db_user.id,
                    email=db_user.email,
                    name=db_user.name,
                    created_at=db_user.created_at
                )
            return None
        finally:
            db.close()

    def create_user(self, user: User) -> User:
        db = self._get_db()
        try:
            db_user = DBUser(
                email=user.email,
                name=user.name,
                password_hash="",  # Will be set separately
                created_at=user.created_at
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)  # Get the auto-generated ID
            
            # Return user with the generated ID
            user.id = db_user.id
            return user
        finally:
            db.close()

    def get_user_password_hash(self, email: str) -> Optional[str]:
        db = self._get_db()
        try:
            db_user = db.query(DBUser).filter(DBUser.email == email).first()
            return db_user.password_hash if db_user else None
        finally:
            db.close()

    def set_user_password_hash(self, email: str, password_hash: str):
        db = self._get_db()
        try:
            db_user = db.query(DBUser).filter(DBUser.email == email).first()
            if db_user:
                db_user.password_hash = password_hash
                db.commit()
        finally:
            db.close()

    # Account methods
    def get_accounts(self) -> List[Account]:
        db = self._get_db()
        try:
            db_accounts = db.query(DBAccount).all()
            return [Account(
                id=acc.id,
                uuid=str(acc.uuid),
                name=acc.name,
                balance=acc.balance,
                user_id=acc.user_id
            ) for acc in db_accounts]
        finally:
            db.close()

    def get_accounts_by_user(self, user_id: str) -> List[Account]:
        db = self._get_db()
        try:
            db_accounts = db.query(DBAccount).filter(DBAccount.user_id == user_id).all()
            return [Account(
                id=acc.id,
                uuid=str(acc.uuid),
                name=acc.name,
                balance=acc.balance,
                user_id=acc.user_id
            ) for acc in db_accounts]
        finally:
            db.close()

    def get_account(self, account_id: str) -> Optional[Account]:
        db = self._get_db()
        try:
            db_account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
            if db_account:
                return Account(
                    id=db_account.id,
                    uuid=str(db_account.uuid),
                    name=db_account.name,
                    balance=db_account.balance,
                    user_id=db_account.user_id
                )
            return None
        finally:
            db.close()

    def get_account_by_uuid(self, account_uuid: str) -> Optional[Account]:
        db = self._get_db()
        try:
            db_account = db.query(DBAccount).filter(DBAccount.uuid == account_uuid).first()
            if db_account:
                return Account(
                    id=db_account.id,
                    uuid=str(db_account.uuid),
                    name=db_account.name,
                    balance=db_account.balance,
                    user_id=db_account.user_id
                )
            return None
        finally:
            db.close()

    def get_account_by_uuid_and_user(self, account_uuid: str, user_id: str) -> Optional[Account]:
        db = self._get_db()
        try:
            db_account = db.query(DBAccount).filter(
                DBAccount.uuid == account_uuid,
                DBAccount.user_id == user_id
            ).first()
            if db_account:
                return Account(
                    id=db_account.id,
                    uuid=str(db_account.uuid),
                    name=db_account.name,
                    balance=db_account.balance,
                    user_id=db_account.user_id
                )
            return None
        finally:
            db.close()

    def get_account_by_user(self, account_id: str, user_id: str) -> Optional[Account]:
        db = self._get_db()
        try:
            db_account = db.query(DBAccount).filter(
                DBAccount.id == account_id,
                DBAccount.user_id == user_id
            ).first()
            if db_account:
                return Account(
                    id=db_account.id,
                    uuid=str(db_account.uuid),
                    name=db_account.name,
                    balance=db_account.balance,
                    user_id=db_account.user_id
                )
            return None
        finally:
            db.close()

    def add_account(self, account: CreateAccount) -> Account:
        db = self._get_db()
        try:
            db_account = DBAccount(
                name=account.name,
                balance=account.balance,
                user_id=account.user_id
            )
            db.add(db_account)
            db.commit()
            db.refresh(db_account)  # Get the auto-generated ID
            
            # Return account with the generated ID and UUID
            return Account(
                id=db_account.id,
                uuid=str(db_account.uuid),
                name=account.name,
                balance=account.balance,
                user_id=account.user_id
            )
        finally:
            db.close()
    
    def update_account_balance(self, account_id: str, new_balance: float):
        db = self._get_db()
        try:
            db_account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
            if db_account:
                db_account.balance = new_balance
                db.commit()
        finally:
            db.close()

    # Transaction methods
    def get_transactions(self, account_id: Optional[str] = None) -> List[Transaction]:
        db = self._get_db()
        try:
            query = db.query(DBTransaction)
            if account_id:
                query = query.filter(DBTransaction.account_id == account_id)

            db_transactions = query.order_by(DBTransaction.timestamp.desc()).all()
            return [Transaction(
                id=txn.id,
                account_id=txn.account_id,
                amount=txn.amount,
                merchant=txn.merchant,
                description=txn.description,
                category=txn.category,
                transaction_type=txn.transaction_type,
                timestamp=txn.timestamp
            ) for txn in db_transactions]
        finally:
            db.close()

    def add_transaction(self, transaction: Transaction) -> Transaction:
        db = self._get_db()
        try:
            db_transaction = DBTransaction(
                account_id=transaction.account_id,
                amount=transaction.amount,
                merchant=transaction.merchant,
                description=transaction.description,
                category=transaction.category,
                transaction_type=transaction.transaction_type,
                timestamp=transaction.timestamp
            )
            db.add(db_transaction)
            db.commit()
            db.refresh(db_transaction)  # Get the auto-generated ID
            
            # Return transaction with the generated ID
            transaction.id = db_transaction.id
            return transaction
        finally:
            db.close()

    # TopUp Rules methods
    def get_topup_rules(self, account_id: Optional[str] = None) -> List[TopUpRule]:
        db = self._get_db()
        try:
            query = db.query(DBTopUpRule)
            if account_id:
                query = query.filter(DBTopUpRule.account_id == account_id)

            db_rules = query.all()
            return [TopUpRule(
                id=rule.id,
                account_id=rule.account_id,
                threshold=rule.threshold,
                topup_amount=rule.topup_amount,
                enabled=rule.enabled
            ) for rule in db_rules]
        finally:
            db.close()

    def add_topup_rule(self, rule: TopUpRule) -> TopUpRule:
        db = self._get_db()
        try:
            db_rule = DBTopUpRule(
                account_id=rule.account_id,
                threshold=rule.threshold,
                topup_amount=rule.topup_amount,
                enabled=rule.enabled
            )
            db.add(db_rule)
            db.commit()
            db.refresh(db_rule)  # Get the auto-generated ID
            
            # Return rule with the generated ID
            rule.id = db_rule.id
            return rule
        finally:
            db.close()

    # TopUp Events methods
    def get_topup_events(self, account_id: Optional[str] = None) -> List[TopUpEvent]:
        db = self._get_db()
        try:
            query = db.query(DBTopUpEvent)
            if account_id:
                query = query.filter(DBTopUpEvent.account_id == account_id)

            db_events = query.order_by(DBTopUpEvent.timestamp.desc()).all()
            return [TopUpEvent(
                id=event.id,
                account_id=event.account_id,
                amount=event.amount,
                triggered_balance=event.triggered_balance,
                timestamp=event.timestamp
            ) for event in db_events]
        finally:
            db.close()

    def add_topup_event(self, event: TopUpEvent) -> TopUpEvent:
        db = self._get_db()
        try:
            db_event = DBTopUpEvent(
                account_id=event.account_id,
                amount=event.amount,
                triggered_balance=event.triggered_balance,
                timestamp=event.timestamp
            )
            db.add(db_event)
            db.commit()
            db.refresh(db_event)  # Get the auto-generated ID
            
            # Return event with the generated ID
            event.id = db_event.id
            return event
        finally:
            db.close()

# Create singleton instance
db = SQLiteRepository()
