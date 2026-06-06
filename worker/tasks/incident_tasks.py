from worker.celery_app import celery_app
from agent.state import IncidentState
from agent.graph import workflow
import structlog

logger = structlog.get_logger()

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p1")
def investigate_p1(self, incident_id: str, alert_payload: dict):
    logger.info("P1 investigation started", incident_id=incident_id)
    try:
        initial_state = {
            "incident_id": incident_id,
            "alert_payload": alert_payload,
            "environment": alert_payload.get("environment"),
            "severity": alert_payload.get("severity"),
            "affected_service": alert_payload.get("affected_service"),
            "alert_timestamp": alert_payload.get("timestamp"),
            "retry_count": 0,
            "errors": [],
            "current_status": "investigating",
            "messages": []
        }
        result = workflow.invoke(initial_state)
        logger.info(f"Workflow completed", result_keys=list(result.keys()) if result else None)
        return {"incident_id": incident_id, "status": "completed"}
    except Exception as e:
        logger.error(f"Investigation failed: {str(e)}", incident_id=incident_id)
        raise

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p2")
def investigate_p2(self, incident_id: str, alert_payload: dict):
    logger.info("P2 investigation started", incident_id=incident_id)
    initial_state = {
        "incident_id": incident_id,
        "alert_payload": alert_payload,
        "environment": alert_payload.get("environment"),
        "severity": alert_payload.get("severity"),
        "affected_service": alert_payload.get("affected_service"),
        "alert_timestamp": alert_payload.get("timestamp"),
        "retry_count": 0,
        "errors": [],
        "current_status": "investigating",
        "messages": []
    }
    workflow.invoke(initial_state)
    return {"incident_id": incident_id, "status": "completed"}

@celery_app.task(bind=True, max_retries=3, name="worker.tasks.incident_tasks.investigate_p3")
def investigate_p3(self, incident_id: str, alert_payload: dict):
    logger.info("P3 investigation started", incident_id=incident_id)
    initial_state = {
        "incident_id": incident_id,
        "alert_payload": alert_payload,
        "environment": alert_payload.get("environment"),
        "severity": alert_payload.get("severity"),
        "affected_service": alert_payload.get("affected_service"),
        "alert_timestamp": alert_payload.get("timestamp"),
        "retry_count": 0,
        "errors": [],
        "current_status": "investigating",
        "messages": []
    }
    workflow.invoke(initial_state)
    return {"incident_id": incident_id, "status": "completed"}
