from agent.state import IncidentState
import requests
import os

teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")

def escalate(state: IncidentState) -> dict:

    incident_id = state.get("incident_id")
    approval_status = state.get("approval_status")
    root_cause_summary = state.get("root_cause_summary")
    severity = state.get("severity")

    requests.post(teams_webhook, json={
        "text": f"🚨 Incident {incident_id} — P{severity} — escalated\n"
                f"Root cause: {root_cause_summary}\n"
                f"Needs manual review"
        })

    return {
        "current_status": "escalated"
    }