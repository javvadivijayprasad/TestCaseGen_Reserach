"""Minimal retail banking reference API used as a mutation-testing target."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Customer:
    id: int
    verified: bool = False
    tier: str = "standard"


@dataclass
class Account:
    id: int
    owner_id: int
    kind: str  # checking | savings
    balance: int  # cents
    status: str = "active"  # active | closed


class BankingAPI:
    """In-memory reference retail-banking service."""

    def __init__(self) -> None:
        self.customers: dict[int, Customer] = {}
        self.accounts: dict[int, Account] = {}
        self.daily_internal_transfer_cents: dict[int, int] = {}  # owner_id -> cents today
        self._next_id = 1

    # ---------- Customer ----------
    def create_customer(self, verified: bool = False,
                        tier: str = "standard") -> Customer:
        if tier not in ("standard", "premium"):
            raise ValueError("invalid tier")
        c = Customer(id=self._next_id, verified=verified, tier=tier)
        self.customers[c.id] = c
        self._next_id += 1
        return c

    # ---------- Account open ----------
    def open_checking(self, owner_id: int, initial_deposit_cents: int) -> Account:
        c = self.customers.get(owner_id)
        if not c or not c.verified:
            raise PermissionError("customer not verified")
        # $25 - $50,000 inclusive
        if initial_deposit_cents < 2500 or initial_deposit_cents > 5_000_000:
            raise ValueError("deposit out of range")
        a = Account(id=self._next_id, owner_id=owner_id, kind="checking",
                    balance=initial_deposit_cents)
        self.accounts[a.id] = a
        self._next_id += 1
        return a

    def open_savings(self, owner_id: int, initial_deposit_cents: int) -> Account:
        c = self.customers.get(owner_id)
        if not c or not c.verified:
            raise PermissionError("customer not verified")
        if initial_deposit_cents < 10_000:  # $100
            raise ValueError("initial deposit below minimum")
        a = Account(id=self._next_id, owner_id=owner_id, kind="savings",
                    balance=initial_deposit_cents)
        self.accounts[a.id] = a
        self._next_id += 1
        return a

    # ---------- Transfers ----------
    def transfer_internal(self, source_id: int, target_id: int,
                          amount_cents: int) -> tuple[Account, Account]:
        src = self.accounts.get(source_id)
        tgt = self.accounts.get(target_id)
        if not src or not tgt:
            raise KeyError("unknown account")
        if src.owner_id != tgt.owner_id:
            raise PermissionError("internal transfer requires same owner")
        if src.status != "active" or tgt.status != "active":
            raise ValueError("inactive account")
        if amount_cents <= 0:
            raise ValueError("amount must be positive")
        # daily limit $25,000 = 2_500_000 cents
        current = self.daily_internal_transfer_cents.get(src.owner_id, 0)
        if current + amount_cents > 2_500_000:
            raise ValueError("daily transfer limit exceeded")
        if src.balance < amount_cents:
            raise ValueError("insufficient funds")
        src.balance -= amount_cents
        tgt.balance += amount_cents
        self.daily_internal_transfer_cents[src.owner_id] = current + amount_cents
        return src, tgt

    def transfer_recurring_schedule(self, customer_id: int,
                                    amount_cents: int, frequency: str) -> dict:
        c = self.customers.get(customer_id)
        if not c:
            raise KeyError("unknown customer")
        if frequency not in ("weekly", "biweekly", "monthly"):
            raise ValueError("unsupported frequency")
        cap = 1_000_000 if c.tier == "premium" else 250_000
        if amount_cents <= 0 or amount_cents > cap:
            raise ValueError("per-occurrence amount out of range")
        return {"customer_id": customer_id, "amount_cents": amount_cents,
                "frequency": frequency, "status": "scheduled"}

    # ---------- Account close ----------
    def close_account(self, account_id: int) -> Account:
        a = self.accounts.get(account_id)
        if not a:
            raise KeyError("unknown account")
        if a.balance != 0:
            raise ValueError("balance must be zero to close without sweep")
        a.status = "closed"
        return a

    # ---------- Interest (savings) ----------
    @staticmethod
    def savings_tier_rate_bps(balance_cents: int) -> int:
        """Return tier interest rate in basis points (bps=1/100 of percent)."""
        if balance_cents < 100_000:   # < $1,000
            return 10
        if balance_cents < 1_000_000:  # < $10,000
            return 50
        if balance_cents < 10_000_000:  # < $100,000
            return 150
        return 250
