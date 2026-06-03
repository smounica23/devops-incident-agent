from fastapi import APIRouter, Depends, HTTPException
from api.schemas.alerts import AlertPayload
from sqlalchemy.orm import Session
from db.models import Incident, IncidentStatus, SeverityLevel
from db.database import get_db
import uuid
from worker.tasks.incident_tasks import investigate_p1, investigate_p2, investigate_p3
from datetime import datetime, timezone
import redis
import os

router = APIRouter()
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

SEVERITY_MAP = {
    "critical": "P1",
    "high": "P1",
    "medium": "P2",
    "low": "P3",
    "warning": "P2",
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3"
}


@router.post("/alerts")
def post_alerts(request:AlertPayload,
                db : Session = Depends(get_db)):

    incident_id = "INC-" + str(uuid.uuid4())[:8].upper()
    normalized = SEVERITY_MAP.get(request.severity.strip().lower(), "P2")

    alerts = Incident(
        id = incident_id,
        status = IncidentStatus.RECEIVED,
        severity = SeverityLevel[normalized],
        alert_payload = request.model_dump(),
        environment = request.environment,
        affected_service = request.affected_service,
        alert_timestamp = request.timestamp or datetime.now(timezone.utc)
    )

    db.add(alerts)
    db.commit()
    db.refresh(alerts)

    if normalized  == "P0":

        return {
            "incident_id": incident_id,
            "status": "P0 fast path — paging on-call immediately",
            "severity": normalized
        }
    
    elif normalized == "P1":
        investigate_p1.delay(incident_id, request.model_dump())
    
    elif normalized == "P2":
        investigate_p2.delay(incident_id, request.model_dump())

    elif normalized == "P3":
        investigate_p3.delay(incident_id, request.model_dump())

    return {
    "incident_id": incident_id,
    "status": "received",
    "message": f"Incident {incident_id} queued for investigation",
    "severity": normalized
}

def get_incident_or_404(incident_id: str, db: Session) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/incidents/{incident_id}")
def getIncidentById(incident_id: str,
                    db : Session = Depends(get_db)):

    incident = get_incident_or_404(incident_id, db)
    return incident


@router.post("/incidents/{incident_id}/approve")
def approveIncident(incident_id: str,
                    db : Session = Depends(get_db)):
    incident = get_incident_or_404(incident_id, db)
    incident.status = IncidentStatus.FIX_APPROVED
    db.commit()
    redis_client.setex(
        f"hitl:approval:{incident_id}",  
        3600,                             
        "approved"                        
    )
    return {"message": "Approval recorded"}

@router.post("/incidents/{incident_id}/reject")
def rejectIncident(incident_id: str,
                    db : Session = Depends(get_db)):
    
    incident = get_incident_or_404(incident_id, db)
    incident.status = IncidentStatus.FIX_REJECTED
    db.commit()
    redis_client.setex(
        f"hitl:approval:{incident_id}",  
        3600,                             
        "rejected"                        
    )
    return {"message": "Approval denied"}

