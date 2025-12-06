import time
from random import SystemRandom as Random
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=3)
def send_notification_task(self, tr_id: str, to_wallet_id: int):
    try:
        logger.info(
            "Sending notification for tr_id=%s to wallet=%s", tr_id, to_wallet_id
        )
        time.sleep(5)

        if Random().random() < 0.3:
            raise RuntimeError("Simulated notification failure")

        logger.info("Notification sent for tr_id=%s", tr_id)
        return {"tr_id": tr_id, "to_wallet": to_wallet_id, "status": "sent"}
    except Exception as exc:
        logger.exception("Notification failed, will retry")
        raise self.retry(exc=exc)
