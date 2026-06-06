from agent.state import IncidentState
import os
import requests
import redis
import time

teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")

redis_client = redis.from_url(os.getenv("REDIS_URL"))


def human_approval(state: IncidentState) -> dict:

    incident_id = state.get("incident_id")
    fix_pr_url = state.get("fix_pr_url")
    root_cause_summary = state.get("root_cause_summary")
    severity = state.get("severity")

    redis_client.setex(f"hitl:approval:{incident_id}", 1800, "pending")

    requests.post(teams_webhook, json={
    "text": f"🚨 Incident {incident_id} — P{severity} — Fix PR ready\n"
            f"Root cause: {root_cause_summary}\n"
            f"PR: {fix_pr_url}\n"
            f"Approve: POST /api/v1/incidents/{incident_id}/approve\n"
            f"Reject: POST /api/v1/incidents/{incident_id}/reject"
    })

    timeout = int(os.getenv("HITL_TIMEOUT_P1", 900))
    elapsed = 0


    while elapsed < timeout:
        decision = redis_client.get(f"hitl:approval:{incident_id}")
        if decision and decision.decode() != "pending":
            return {
                "approval_status": decision.decode(),
                "current_status": "fix_approved" if decision.decode() == "approved" else "fix_rejected"
            }
    
        time.sleep(5)
        elapsed += 5  
    return {
        "approval_status": "timeout",
        "current_status": "escalated"
    }