from unittest import mock

from transfer.tasks import send_notification_task
from transfer.services.transaction_service import TransactionService


class TestTransactionServiceNotification:
    @mock.patch.object(send_notification_task, "delay")
    def test_it_calls_task_on_notification(self, mock_delay):
        TransactionService.send_notification(tr_id=55, target_wallet=777)

        mock_delay.assert_called_once_with("55", 777)
