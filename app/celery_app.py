import os

from celery import Celery

from env import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
app.conf.result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

app.autodiscover_tasks()
