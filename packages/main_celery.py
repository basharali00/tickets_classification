from celery import Celery

from packages.settings import settings

app = Celery(
    "tickets",
    broker_url=settings.REDIS_URL,
    include=[
        "packages.classification.tasks.classify_ticket_task",
        "packages.classification.tasks.periodic_classify_tickets_task",
    ],
)
