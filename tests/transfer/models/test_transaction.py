import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from transfer.models import Transaction
from tests.transfer.factories import WalletFactory, TransactionFactory

from django_extended.constants import MINIMUM_TRANSFER_RATE


@pytest.mark.django_db
class TestTransactionModel:
    def test_it_raises_error_if_amount_is_less_than_minimum_rate(self):
        wallet_from = WalletFactory()
        wallet_to = WalletFactory()

        with pytest.raises(ValidationError) as exc:
            TransactionFactory(
                from_wallet=wallet_from,
                to_wallet=wallet_to,
                amount=MINIMUM_TRANSFER_RATE - Decimal("0.01"),
            )

        assert "amount" in exc.value.message_dict
        assert "minimum amount" in exc.value.message_dict["amount"][0].lower()

    def test_it_creates_transaction_when_amount_is_valid(self):
        wallet_from = WalletFactory()
        wallet_to = WalletFactory()

        tx = TransactionFactory(
            from_wallet=wallet_from,
            to_wallet=wallet_to,
            amount=MINIMUM_TRANSFER_RATE,
        )

        assert isinstance(tx, Transaction)
        assert tx.amount == MINIMUM_TRANSFER_RATE
        assert tx.from_wallet == wallet_from
        assert tx.to_wallet == wallet_to
