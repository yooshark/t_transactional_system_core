from decimal import Decimal, ROUND_DOWN

from django.db import transaction
from django.db.models import Q

from transfer.dto import TransferDto
from transfer.models import Wallet, Transaction
from django_extended.exceptions import TransactionError
from django_extended.enums import TransactionStatusType
from transfer.tasks import send_notification_task


class TransactionService:
    TECH_WALLET_OWNER = "tech_admin"

    def __init__(self, dto: TransferDto) -> None:
        self.dto = dto
        self.init_amount: Decimal = dto.amount

    @staticmethod
    def _validate_balance(from_wallet: Wallet, total_debit: Decimal) -> None:
        if from_wallet.balance < total_debit:
            raise TransactionError("Not enough balance")

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    @staticmethod
    def send_notification(self, tr_id: int, target_wallet: int) -> None:
        send_notification_task.delay(str(tr_id), target_wallet)

    def transfer(self) -> Transaction:
        commission = self._calculate_commission()
        total_debit = self._quantize(self.init_amount + commission)
        return self.handle_wallet_transactions(commission, total_debit)

    def handle_wallet_transactions(
        self, commission: Decimal, total_debit: Decimal
    ) -> Transaction:
        with transaction.atomic():
            from_wallet, to_wallet, tech_wallet = self._load_wallets()
            self._validate_balance(from_wallet, total_debit)
            self._apply_balance_updates(
                from_wallet, to_wallet, tech_wallet, total_debit, commission
            )
            return self._create_transaction(
                from_wallet, to_wallet, commission, total_debit
            )

    def _load_wallets(self) -> tuple[Wallet, ...]:
        wallets = list(
            Wallet.objects.select_for_update().filter(
                Q(id__in=[self.dto.from_wallet_id, self.dto.to_wallet_id])
                | Q(owner=self.TECH_WALLET_OWNER)
            )
        )

        if len(wallets) < 3:
            raise TransactionError("Required wallets not found")

        from_wallet = next(
            (w for w in wallets if w.id == self.dto.from_wallet_id), None
        )
        to_wallet = next((w for w in wallets if w.id == self.dto.to_wallet_id), None)
        tech_wallet = next(
            (w for w in wallets if w.owner == self.TECH_WALLET_OWNER), None
        )

        if from_wallet is None:
            raise TransactionError("From-wallet not found")
        if to_wallet is None:
            raise TransactionError("To-wallet not found")
        if tech_wallet is None:
            raise TransactionError("Tech-wallet not found")

        return (
            from_wallet,
            to_wallet,
            tech_wallet,
        )

    def _calculate_commission(self) -> Decimal:
        return (
            (self.init_amount * Decimal("0.10")).quantize(Decimal("0.01"))
            if self.init_amount > Decimal("1000.00")
            else Decimal("0.00")
        )

    def _calculate_total_debit(self, commission: Decimal) -> Decimal:
        return (self.init_amount + commission).quantize(
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
        to_wallet.balance += self.init_amount
        tech_wallet.balance += commission

        Wallet.objects.bulk_update(
            [from_wallet, to_wallet, tech_wallet],
            ["balance"],
        )

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
            amount=self.init_amount,
            commission=commission,
            total_debit=total_debit,
            status=TransactionStatusType.SUCCESS,
        )
