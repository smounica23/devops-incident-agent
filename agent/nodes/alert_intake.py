from agent.state import IncidentState
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    "critical": "P1",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
    "warning": "P2",
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3",
}


def alert_intake(state: IncidentState) -> dict:

    alert_payload = state.get("alert_payload", {})

    if not isinstance(alert_payload, dict):
        raise ValueError("alert_payload must be a dictionary")

    alert_id = alert_payload.get("incident_id")
    raw_severity = alert_payload.get("severity", "medium")
    affected_service = alert_payload.get("affected_service")
    environment = alert_payload.get("environment", "unknown")
    normalized_severity = SEVERITY_MAP.get(
        str(raw_severity).strip().lower(),
        "P2"
    )

    alert_timestamp = alert_payload.get("timestamp")

    if not alert_timestamp:
        alert_timestamp = datetime.now(timezone.utc).isoformat()

    current_status = "investigating"

    logger.info(f"Alert intake - incident: {alert_id}, service: {affected_service}, severity: {normalized_severity}")

    return {
    "severity": normalized_severity,
    "environment": environment,
    "affected_service": affected_service,
    "alert_timestamp": alert_timestamp,
    "current_status": current_status,
    }