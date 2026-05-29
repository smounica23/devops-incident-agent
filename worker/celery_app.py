from celery import Celery
import os

celery_app = Celery(
    "incident_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    include=["worker.tasks.incident_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "worker.tasks.incident_tasks.investigate_p1": {"queue": "p1_incidents"},
        "worker.tasks.incident_tasks.investigate_p2": {"queue": "p2_incidents"},
        "worker.tasks.incident_tasks.investigate_p3": {"queue": "p3_incidents"},
    },
    task_queue_max_priority=10,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
