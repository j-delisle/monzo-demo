from models import Account, Transaction, TopUpRule, TopUpEvent, User
from datetime import datetime
from typing import List, Optional
import uuid

class InMemoryDatabase:
    def __init__(self):
        # Demo users with hashed passwords
        self.users: List[User] = [
            User(
                id="user_1",
                email="demo@monzo.com",
                name="Demo User",
                created_at=datetime.now()
            ),
            User(
                id="user_2",
                email="john@example.com",
                name="John Doe",
                created_at=datetime.now()
            )
        ]
        # Store hashed passwords separately (in real app would be in User model)
        self.user_passwords = {
            "demo@monzo.com": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "demo"
            "john@example.com": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"   # "demo"
        }

        self.accounts: List[Account] = [
            Account(id="acc_1", name="Current Account", balance=150.50, user_id="user_1"),
            Account(id="acc_2", name="Savings Account", balance=1250.00, user_id="user_1"),
            Account(id="acc_3", name="Current Account", balance=89.23, user_id="user_2"),
        ]
        self.transactions: List[Transaction] = []
        self.topup_rules: List[TopUpRule] = []
        self.topup_events: List[TopUpEvent] = []

    def get_accounts(self) -> List[Account]:
        return self.accounts

    def get_account(self, account_id: str) -> Optional[Account]:
        return next((acc for acc in self.accounts if acc.id == account_id), None)

    def update_account_balance(self, account_id: str, new_balance: float):
        account = self.get_account(account_id)
        if account:
            account.balance = new_balance

    def get_transactions(self, account_id: Optional[str] = None) -> List[Transaction]:
        if account_id:
            return [t for t in self.transactions if t.account_id == account_id]
        return self.transactions

    def add_transaction(self, transaction: Transaction) -> Transaction:
        self.transactions.append(transaction)
        return transaction

    def get_topup_rules(self, account_id: Optional[str] = None) -> List[TopUpRule]:
        if account_id:
            return [r for r in self.topup_rules if r.account_id == account_id]
        return self.topup_rules

    def add_topup_rule(self, rule: TopUpRule) -> TopUpRule:
        self.topup_rules.append(rule)
        return rule

    def get_topup_events(self, account_id: Optional[str] = None) -> List[TopUpEvent]:
        if account_id:
            return [e for e in self.topup_events if e.account_id == account_id]
        return self.topup_events

    def add_topup_event(self, event: TopUpEvent) -> TopUpEvent:
        self.topup_events.append(event)
        return event

    # User methods
    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.users if user.email == email), None)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((user for user in self.users if user.id == user_id), None)

    def create_user(self, user: User) -> User:
        self.users.append(user)
        return user

    def get_user_password_hash(self, email: str) -> Optional[str]:
        return self.user_passwords.get(email)

    def set_user_password_hash(self, email: str, password_hash: str):
        self.user_passwords[email] = password_hash

    # User-filtered methods
    def get_accounts_by_user(self, user_id: str) -> List[Account]:
        return [acc for acc in self.accounts if acc.user_id == user_id]

    def get_account_by_user(self, account_id: str, user_id: str) -> Optional[Account]:
        account = self.get_account(account_id)
        if account and account.user_id == user_id:
            return account
        return None

db = InMemoryDatabase()
