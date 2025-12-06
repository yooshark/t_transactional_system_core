import pytest
from unittest import mock
from decimal import Decimal

from transfer.tasks import send_notification_task
from tests.transfer.factories import WalletFactory


@pytest.mark.django_db
class TestPost:
    @mock.patch.object(send_notification_task, "delay")
    def test_it_sends_notification_after_successful_transfer(self, mock_delay, api_client):
        from_wallet = WalletFactory(balance=Decimal("1000"))
        to_wallet = WalletFactory(balance=Decimal("0"))

        payload = {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "100.00",
        }

        response = api_client.post("/api/transfer/", data=payload, format="json")

        assert response.status_code == 201
        mock_delay.assert_called_once()

    @mock.patch.object(send_notification_task, "delay")
    def test_it_does_not_send_notification_if_transfer_fails(self, mock_delay, api_client):
        from_wallet = WalletFactory(balance=Decimal("0"))
        to_wallet = WalletFactory(balance=Decimal("0"))

        payload = {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "100.00",
        }

        response = api_client.post("/api/transfer/", data=payload, format="json")

        assert response.status_code == 400
        mock_delay.assert_not_called()
