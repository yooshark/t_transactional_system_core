import pytest
from unittest import mock

from transfer.tasks import send_notification_task


@pytest.mark.django_db
class TestSendNotificationTask:
    @mock.patch("transfer.tasks.time.sleep", return_value=None)
    def test_it_returns_success_on_first_try(self, mock_sleep):
        with mock.patch("transfer.tasks.Random.random", return_value=0.8):
            result = send_notification_task("1", 10)

        assert result == {"tr_id": "1", "to_wallet": 10, "status": "sent"}
        mock_sleep.assert_called_once()  # <-- теперь проверяем, что sleep вызвался

    @mock.patch("transfer.tasks.time.sleep", return_value=None)
    def test_it_retries_on_failure(self, mock_sleep):
        with mock.patch("transfer.tasks.Random.random", return_value=0.1):
            task = send_notification_task

            with pytest.raises(Exception):
                task("1", 10)

        mock_sleep.assert_called_once()

    @mock.patch("transfer.tasks.time.sleep", return_value=None)
    def test_it_retries_exact_number_of_times(self, mock_sleep):
        with mock.patch("transfer.tasks.Random.random", return_value=0.1):
            task = send_notification_task

            task.retry = mock.Mock(side_effect=Exception("retry"))

            with pytest.raises(Exception):
                task("1", 10)

            assert task.retry.call_count == 1
            mock_sleep.assert_called_once()
