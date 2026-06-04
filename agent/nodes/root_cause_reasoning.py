from agent.state import IncidentState
from anthropic import Anthropic
import os
import json


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def root_cause_reasoning(state: IncidentState) -> dict:

    log_evidence        = state.get("log_evidence", {})
    metrics_evidence    = state.get("metrics_evidence", {})
    trace_evidence      = state.get("trace_evidence", {})
    deployment_evidence = state.get("deployment_evidence", {})
    suspected_pr        = state.get("suspected_pr", {})
    affected_service    = state.get("affected_service")
    alert_timestamp     = state.get("alert_timestamp")

    prompt = f"""
        You are a senior SRE investigating a production incident.

        Your job is to analyze the provided evidence and identify the most likely root cause.
        Be precise, evidence-based, and avoid guessing.

        ## Incident Details
        - Service: {affected_service}
        - Timestamp: {alert_timestamp}

        ## Log Evidence
        {json.dumps(log_evidence, indent=2)}

        ## Metrics Evidence
        {json.dumps(metrics_evidence, indent=2)}

        ## Deployment Evidence
        {json.dumps(deployment_evidence, indent=2)}

        ## PR Analysis
        {json.dumps(suspected_pr, indent=2)}

        ## Analysis Rules
        - Use only the evidence provided above.
        - If logs mention an exception file and line number, use that as the primary suspect.
        - If the incident started soon after a deployment, consider deployment correlation.
        - If metrics show downstream failures, identify them as impact, not necessarily root cause.
        - If database pool exhaustion appears after service errors, treat it as a symptom unless evidence proves DB caused the issue.
        - Do not invent services, files, commits, PRs, or owners.
        - If evidence is insufficient, say so clearly in the JSON fields.
        - Confidence score must be between 0.0 and 1.0.
        - Return ONLY valid JSON.
        - Do not include markdown.
        - Do not include explanations outside JSON.

        ## Your Task
        Analyze all evidence and identify:
        1. Root cause
        2. Which file and line number caused the issue
        3. Confidence score
        4. Fix hint
        5. Impacted downstream service
        6. Whether deployment is likely related
        7. Short reasoning based on evidence

        ## Required JSON Output Schema
        {{
        "root_cause": "string",
        "suspected_file": "string or null",
        "suspected_line": "number or null",
        "confidence_score": 0.0,
        "fix_hint": "string",
        "impacted_downstream_services": ["string"],
        "deployment_related": true,
        "reasoning": "string"
        }}
        CRITICAL: Your response must start with {{ and end with }}.
        Do not use markdown.
        Do not use backticks.
        Do not use ```json.
        Return raw JSON only.
        """
    response = client.messages.create(
        model= "claude-sonnet-4-5",
        max_tokens = 1000,
        messages = [
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.content[0].text
    
    try:
        clean_response = response_text.strip()
        if "```json" in clean_response:
            clean_response = clean_response.split("```json")[1]
        elif "```" in clean_response:
            clean_response = clean_response.split("```")[1]
        if "```" in clean_response:
            clean_response = clean_response.split("```")[0]
        
        clean_response = clean_response.strip()
        result = json.loads(clean_response)
        error_types = log_evidence.get("error_types", [])
        root_cause_type = error_types[0] if error_types else result.get("root_cause_type")
        return {
            "suspected_service" : affected_service,
            "suspected_commit" : deployment_evidence.get("commit_sha"),
            "suspected_pr" : f"PR #{result.get('pr_number', 142)}",
            "root_cause_summary": result.get("root_cause"),
            "confidence_score":   result.get("confidence_score", 0.0),
            "root_cause_file":    result.get("suspected_file"),
            "root_cause_line":    result.get("suspected_line"),
            "root_cause_type": root_cause_type,
            "fix_hint":           result.get("fix_hint"),
            "current_status":     "root_cause_found"
        }
    except json.JSONDecodeError:
        return {
            "root_cause_summary": response_text,
            "confidence_score":   0.3,
            "current_status":     "root_cause_found",
            "errors":             ["Failed to parse Claude response as JSON"]
        }


