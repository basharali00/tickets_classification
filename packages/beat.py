from celery.schedules import crontab

from packages.main_celery import app

app.conf.beat_schedule = {
    "periodic_classify_tickets_task": {
        "task": "packages.classification.tasks.periodic_classify_tickets_task.periodic_classify_tickets_task",
        "schedule": crontab(minute="*/10"),  # every 10 minutes
    },
}
