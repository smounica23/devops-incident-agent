from agent.state import IncidentState
import os
import json
import requests
import base64

def confluence_documentation(state: IncidentState) -> dict:

    incident_id = state.get("incident_id")
    severity = state.get("severity")
    affected_service = state.get("affected_service")
    root_cause_summary = state.get("root_cause_summary")
    root_cause_file = state.get("root_cause_file")
    root_cause_line = state.get("root_cause_line")
    fix_pr_url = state.get("fix_pr_url")
    log_evidence = state.get("log_evidence", {})
    confidence_score = state.get("confidence_score")
    merge_status = state.get("merge_status")

    page_content = f"""
<h2>Incident Summary</h2>
<ul>
<li>Incident ID: {incident_id}</li>
<li>Severity: {severity}</li>
<li>Affected Service: {affected_service}</li>
<li>Merge Status: {merge_status}</li>
</ul>
<h2>Root Cause</h2>
<p>{root_cause_summary}</p>
<ul>
<li>File: {root_cause_file}</li>
<li>Line: {root_cause_line}</li>
<li>Confidence: {confidence_score}</li>
</ul>
<h2>Fix Applied</h2>
<p>PR: <a href="{fix_pr_url}">{fix_pr_url}</a></p>
<h2>Evidence</h2>
<pre>{json.dumps(log_evidence, indent=2)}</pre>
<h2>Preventive Actions</h2>
<ul>
<li>Add null checks for all payment objects</li>
<li>Add unit tests for null payment scenarios</li>
</ul>
<h2>Lessons Learned</h2>
<ul>
<li>Automated incident response reduced MTTR significantly</li>
<li>Deployment correlation helped identify root cause quickly</li>
</ul>
"""

    auth = base64.b64encode(
        f"{os.getenv('ATLASSIAN_EMAIL')}:{os.getenv('ATLASSIAN_API_TOKEN')}".encode()
    ).decode()

    response = requests.post(
        f"{os.getenv('ATLASSIAN_URL')}/wiki/rest/api/content",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        },
        json={
            "type": "page",
            "title": f"Post-Incident Report — {incident_id}",
            "space": {"key": os.getenv("CONFLUENCE_SPACE_KEY")},
            "body": {
                "storage": {
                    "value": page_content,
                    "representation": "storage"
                }
            }
        }
    )

    if response.status_code == 200:
        page_id = response.json().get("id")
        confluence_url = f"{os.getenv('ATLASSIAN_URL')}/wiki/spaces/Incidents/pages/{page_id}"
    else:
        confluence_url = f"Error: {response.status_code} - {response.text}"

    return {
        "confluence_url": confluence_url,
        "current_status": "confluence_created"
    }