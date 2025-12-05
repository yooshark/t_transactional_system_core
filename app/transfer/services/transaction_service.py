from decimal import Decimal, ROUND_DOWN
from typing import Tuple

from django.db import transaction

from transfer.dto import TransferDto
from transfer.models import Wallet, Transaction
from django_extended.exceptions import TransactionError
from django_extended.enums import TransactionStatusType


class TransactionService:
    TECH_WALLET_OWNER = "tech_admin"

    def __init__(self, dto: TransferDto) -> None:
        self.dto = dto

    @transaction.atomic
    def transfer(self) -> Transaction:
        from_wallet, to_wallet, tech_wallet = self._load_wallets()

        self._validate_balance(from_wallet)

        commission = self._calculate_commission()
        total_debit = self._calculate_total_debit(commission)

        self._apply_balance_updates(from_wallet, to_wallet, tech_wallet, commission)

        return self._create_transaction(from_wallet, to_wallet, commission, total_debit)

    def _load_wallets(self) -> Tuple[Wallet, ...]:
        wallet_ids = [self.dto.from_wallet_id, self.dto.to_wallet_id]

        wallets = Wallet.objects.select_for_update().filter(
            id__in=wallet_ids
        ) | Wallet.objects.select_for_update().filter(owner=self.TECH_WALLET_OWNER)

        wallet_map = {w.id: w for w in wallets}
        tech_wallet = next(
            (w for w in wallets if w.owner == self.TECH_WALLET_OWNER), None
        )

        if self.dto.from_wallet_id not in wallet_map:
            raise TransactionError("From-wallet not found")
        if self.dto.to_wallet_id not in wallet_map:
            raise TransactionError("To-wallet not found")
        if tech_wallet is None:
            raise TransactionError("Tech-wallet not found")

        return (
            wallet_map[self.dto.from_wallet_id],
            wallet_map[self.dto.to_wallet_id],
            tech_wallet,
        )

    def _validate_balance(self, from_wallet: Wallet) -> None:
        if from_wallet.balance < self.dto.amount:
            raise TransactionError("Insufficient funds")

    def _calculate_commission(self) -> Decimal:
        amount = self.dto.amount
        if amount > Decimal("1000.00"):
            return (amount * Decimal("0.10")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def _calculate_total_debit(self, commission: Decimal) -> Decimal:
        return (self.dto.amount + commission).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

    def _apply_balance_updates(
        self, from_wallet, to_wallet, tech_wallet, commission
    ) -> None:
        amount = self.dto.amount
        from_wallet.balance -= amount
        to_wallet.balance += amount - commission
        tech_wallet.balance += commission

        from_wallet.save(update_fields=["balance"])
        to_wallet.save(update_fields=["balance"])
        tech_wallet.save(update_fields=["balance"])

    def _create_transaction(
        self, from_wallet, to_wallet, commission, total_debit
    ) -> Transaction:
        return Transaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=self.dto.amount,
            commission=commission,
            total_debit=total_debit,
            status=TransactionStatusType.SUCCESS,
        )
