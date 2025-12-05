import time
from decimal import Decimal, ROUND_DOWN

from django.db import transaction

from transfer.dto import TransferDto
from transfer.models import Wallet, Transaction
from django_extended.exceptions import TransactionError
from django_extended.enums import TransactionStatusType
from transfer.tasks import send_notification_task


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
        time.sleep(0.5)
        self._apply_balance_updates(
            from_wallet, to_wallet, tech_wallet, total_debit, commission
        )

        return self._create_transaction(from_wallet, to_wallet, commission, total_debit)

    def _get_wallets_without_atomic(self):
        return Wallet.objects.filter(
            id__in=[self.dto.from_wallet_id, self.dto.to_wallet_id]
        ) | Wallet.objects.filter(owner=self.TECH_WALLET_OWNER)

    def _get_wallets(self):
        return Wallet.objects.select_for_update().filter(
            id__in=[self.dto.from_wallet_id, self.dto.to_wallet_id]
        ) | Wallet.objects.select_for_update().filter(owner=self.TECH_WALLET_OWNER)

    def _load_wallets(self) -> tuple[Wallet, ...]:
        wallets = self._get_wallets()
        # wallets = self._get_wallets_without_atomic()
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
        print("FROM WALLET BALANCE:", from_wallet.balance, "minus", self.dto.amount)
        if from_wallet.balance < self.dto.amount:
            raise TransactionError("Insufficient funds")

    def _calculate_commission(self) -> Decimal:
        amount: Decimal = self.dto.amount
        if amount > Decimal("1000.00"):
            return (amount * Decimal("0.10")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def _calculate_total_debit(self, commission: Decimal) -> Decimal:
        return (self.dto.amount + commission).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

    def _apply_balance_updates(
        self,
        from_wallet: Wallet,
        to_wallet: Wallet,
        tech_wallet: Wallet,
        total_debit: Decimal,
        commission: Decimal,
    ) -> None:
        from_wallet.balance -= total_debit
        to_wallet.balance += self.dto.amount
        tech_wallet.balance += commission
        time.sleep(0.5)

        from_wallet.save(update_fields=["balance"])
        to_wallet.save(update_fields=["balance"])
        tech_wallet.save(update_fields=["balance"])

    def _create_transaction(
        self,
        from_wallet: Wallet,
        to_wallet: Wallet,
        commission: Decimal,
        total_debit: Decimal,
    ) -> Transaction:
        return Transaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=self.dto.amount,
            commission=commission,
            total_debit=total_debit,
            status=TransactionStatusType.SUCCESS,
        )

    def send_notification(self, tr_id: int, target_wallet: int) -> None:
        send_notification_task.delay(str(tr_id), target_wallet)
