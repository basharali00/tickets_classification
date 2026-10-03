from celery import Celery

from packages.settings import settings

app = Celery("tickets", broker_url=settings.REDIS_URL)
