from agent.state import IncidentState
import requests
import os

teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")

def teams_notification(state: IncidentState) -> dict:

    incident_id = state.get("incident_id")
    severity = state.get("severity")
    affected_service = state.get("affected_service")
    root_cause_summary = state.get("root_cause_summary")
    confluence_url = state.get("confluence_url")
    pr_url = state.get("fix_pr_url")
    current_status = state.get("current_status")

    requests.post(teams_webhook, json={
        "text": f"🚨 Incident {incident_id} — P{severity} — {current_status}\n"
                f"Affected Service {affected_service}\n"
                f"Root cause: {root_cause_summary}\n"
                f"PR_link: {pr_url}\n"
                f"Confluence_Url: {confluence_url}"
    })


    return {
    "teams_notification_status": "sent",
    "current_status": "resolved"
    }