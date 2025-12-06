from decimal import Decimal
from unittest import mock

import pytest
from transfer.services.transaction_service import TransactionService


from tests.transfer.factories import WalletFactory


@pytest.mark.django_db
class TestPost:
    TECH_WALLET_OWNER = "test_admin"

    @mock.patch("transfer.services.transaction_service.TransactionService.DEFAULT_TECH_WALLET_OWNER", new="test_admin")
    def test_it_creates_transaction_successfully(self, api_client):
        from_wallet = WalletFactory(balance=Decimal("2000.00"))
        to_wallet = WalletFactory(balance=Decimal("1000.00"))
        tech_wallet = WalletFactory(owner=self.TECH_WALLET_OWNER, balance=Decimal("0.00"))

        data = {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "1500.00",
        }

        response = api_client.post("/api/transfer/", data=data, format="json")

        assert response.status_code == 201
        from_wallet.refresh_from_db()
        to_wallet.refresh_from_db()
        tech_wallet.refresh_from_db()

        assert from_wallet.balance == Decimal("350.00")
        assert to_wallet.balance == Decimal("2500.00")
        assert tech_wallet.balance == Decimal("150.00")

    def test_it_returns_error_if_insufficient_balance(self, api_client):
        from_wallet = WalletFactory(balance=Decimal("100.00"))
        to_wallet = WalletFactory(balance=Decimal("0.00"))
        WalletFactory(owner=self.TECH_WALLET_OWNER, balance=Decimal("0.00"))

        data = {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "200.00",
        }

        response = api_client.post("/api/transfer/", data=data, format="json")

        assert response.status_code == 400
        assert response.data["detail"] == "Not enough balance"

    def test_it_returns_error_if_wallet_not_found(self, api_client):
        data = {
            "from_wallet_id": 999,
            "to_wallet_id": 1000,
            "amount": "100.00",
        }

        response = api_client.post("/api/transfer/", data=data, format="json")

        assert response.status_code == 400
        assert "not found" in response.data["detail"].lower()

    @mock.patch.object(TransactionService, "transfer")
    def test_it_calls_transaction_service(self, mock_transfer, api_client):
        from_wallet = WalletFactory()
        to_wallet = WalletFactory()

        data = {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "100.00",
        }

        response = api_client.post("/api/transfer/", data=data, format="json")

        assert response.status_code == 201
        mock_transfer.assert_called_once()
