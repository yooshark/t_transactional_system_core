import pytest
from decimal import Decimal
from django.db import transaction

from django_extended.enums import TransactionStatusType
from transfer.models import Wallet
from transfer.dto import TransferDto
from django_extended.exceptions import TransactionError
from transfer.services.transaction_service import TransactionService


@pytest.mark.django_db
class TestTransactionService:
    TECH_WALLET_OWNER = "test_admin"

    def test_successful_transfer(self):
        from_wallet = Wallet.objects.create(owner="user1", balance=Decimal("2000.00"))
        to_wallet = Wallet.objects.create(owner="user2", balance=Decimal("1000.00"))
        tech_wallet = Wallet.objects.create(owner=self.TECH_WALLET_OWNER, balance=Decimal("0.00"))

        dto = TransferDto(
            from_wallet_id=from_wallet.id,
            to_wallet_id=to_wallet.id,
            amount=Decimal("1500.00"),
        )
        service = TransactionService(dto, self.TECH_WALLET_OWNER)
        transaction_obj = service.transfer()

        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()
        tech_wallet.refresh_from_db()

        assert from_wallet.balance == Decimal("350.00")
        assert to_wallet.balance == Decimal("2500.00")
        assert tech_wallet.balance == Decimal("150.00")

        assert transaction_obj.amount == Decimal("1500.00")
        assert transaction_obj.commission == Decimal("150.00")
        assert transaction_obj.total_debit == Decimal("1650.00")
        assert transaction_obj.status == TransactionStatusType.SUCCESS

    def test_insufficient_balance(self):
        from_wallet = Wallet.objects.create(owner="user1", balance=Decimal("100.00"))
        to_wallet = Wallet.objects.create(owner="user2", balance=Decimal("0.00"))
        Wallet.objects.create(owner="test_tech_admin", balance=Decimal("0.00"))

        dto = TransferDto(
            from_wallet_id=from_wallet.id,
            to_wallet_id=to_wallet.id,
            amount=Decimal("200.00"),
        )
        service = TransactionService(dto)

        with pytest.raises(TransactionError, match="Not enough balance"):
            service.transfer()

    def test_transfer_without_commission(self):
        from_wallet = Wallet.objects.create(owner="user1", balance=Decimal("500.00"))
        to_wallet = Wallet.objects.create(owner="user2", balance=Decimal("0.00"))
        tech_wallet = Wallet.objects.create(owner="test_tech_admin", balance=Decimal("0.00"))

        dto = TransferDto(
            from_wallet_id=from_wallet.id,
            to_wallet_id=to_wallet.id,
            amount=Decimal("500.00"),
        )
        service = TransactionService(dto)
        transaction_obj = service.transfer()

        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()
        tech_wallet.refresh_from_db()

        assert transaction_obj.commission == Decimal("0.00")
        assert from_wallet.balance == Decimal("0.00")
        assert to_wallet.balance == Decimal("500.00")
        assert tech_wallet.balance == Decimal("0.00")

    @pytest.mark.django_db(transaction=True)
    def test_concurrent_transfers(self):
        from_wallet = Wallet.objects.create(owner="user1", balance=Decimal("1000.00"))
        to_wallet = Wallet.objects.create(owner="user2", balance=Decimal("0.00"))
        tech_wallet = Wallet.objects.create(owner="test_tech_admin", balance=Decimal("0.00"))

        dto1 = TransferDto(from_wallet_id=from_wallet.id, to_wallet_id=to_wallet.id, amount=Decimal("800"))
        dto2 = TransferDto(from_wallet_id=from_wallet.id, to_wallet_id=to_wallet.id, amount=Decimal("800"))

        service1 = TransactionService(dto1)
        service2 = TransactionService(dto2)

        with transaction.atomic():
            transaction1 = service1.transfer()
            with pytest.raises(TransactionError):
                service2.transfer()

        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()
        tech_wallet.refresh_from_db()

        assert from_wallet.balance >= 0
        assert transaction1.amount == Decimal("800")
