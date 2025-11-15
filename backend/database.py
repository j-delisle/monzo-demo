from models import Account, Transaction, TopUpRule, TopUpEvent
from datetime import datetime
from typing import List, Optional
import uuid

class InMemoryDatabase:
    def __init__(self):
        self.accounts: List[Account] = [
            Account(id="acc_1", name="Current Account", balance=150.50, user_id="user_1"),
            Account(id="acc_2", name="Savings Account", balance=1250.00, user_id="user_1"),
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

db = InMemoryDatabase()