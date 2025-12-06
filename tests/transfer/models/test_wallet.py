import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from tests.transfer.factories import WalletFactory


@pytest.mark.django_db()
class TestWalletModel:
    def test_it_should_raise_error_if_balance_is_negative(self):
        with pytest.raises(ValidationError):
            WalletFactory(balance=Decimal("-1.00"))

    def test_it_should_allow_zero_balance(self):
        wallet = WalletFactory(balance=Decimal("0.00"))
        wallet.refresh_from_db()

        assert wallet.balance == Decimal("0.00")

    def test_it_should_allow_positive_balance(self):
        wallet = WalletFactory(balance=Decimal("150.00"))
        wallet.refresh_from_db()

        assert wallet.balance == Decimal("150.00")

    def test_str_representation(self):
        wallet = WalletFactory(owner="john_doe", balance=Decimal("100.00"))

        assert "john_doe" in str(wallet)
        assert "100.00" in str(wallet)
