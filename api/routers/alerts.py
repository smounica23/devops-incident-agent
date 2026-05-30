from fastapi import APIRouter, Depends, HTTPException
from api.schemas.alerts import AlertPayload
from sqlalchemy.orm import Session
from db.models import Incident, IncidentStatus, SeverityLevel
from db.database import get_db
import uuid
from worker.tasks.incident_tasks import investigate_p1, investigate_p2, investigate_p3
from datetime import datetime, timezone

router = APIRouter()


@router.post("/alerts")
def post_alerts(request:AlertPayload,
                db : Session = Depends(get_db)):

    incident_id = "INC-" + str(uuid.uuid4())[:8].upper()
    alerts = Incident(
        id = incident_id,
        status = IncidentStatus.RECEIVED,
        severity = SeverityLevel[request.severity],
        alert_payload = request.model_dump(),
        environment = request.environment,
        affected_service = request.affected_service,
        alert_timestamp = request.timestamp or datetime.now(timezone.utc)
    )

    db.add(alerts)
    db.commit()
    db.refresh(alerts)

    if request.severity == "P0":

        return {
            "incident_id": incident_id,
            "status": "P0 fast path — paging on-call immediately",
            "severity": request.severity
        }
    
    elif request.severity == "P1":
        investigate_p1.delay(incident_id, request.model_dump())
    
    elif request.severity == "P2":
        investigate_p2.delay(incident_id, request.model_dump())

    elif request.severity == "P3":
        investigate_p3.delay(incident_id, request.model_dump())

    return {
    "incident_id": incident_id,
    "status": "received",
    "message": f"Incident {incident_id} queued for investigation",
    "severity": request.severity
}


@router.get("/incidents/{incident_id}")
def getIncidentById(incident_id: str,
                    db : Session = Depends(get_db)):

    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident





