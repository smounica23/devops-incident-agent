from worker.celery_app import celery_app
import structlog

logger = structlog.get_logger()

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p1")
def investigate_p1(self, incident_id: str, alert_payload: dict):
    logger.info("P1 investigation started", incident_id=incident_id)
    # LangGraph graph will be wired here on Day 3
    return {"incident_id": incident_id, "status": "investigating"}

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p2")
def investigate_p2(self, incident_id: str, alert_payload: dict):
    logger.info("P2 investigation started", incident_id=incident_id)
    return {"incident_id": incident_id, "status": "investigating"}

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p3")
def investigate_p3(self, incident_id: str, alert_payload: dict):
    logger.info("P3 investigation started", incident_id=incident_id)
    return {"incident_id": incident_id, "status": "investigating"}
