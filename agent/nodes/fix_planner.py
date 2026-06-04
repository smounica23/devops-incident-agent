from agent.state import IncidentState
import json
import os
from anthropic import Anthropic


client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def fix_planner(state: IncidentState) -> dict:
    root_cause_file = state.get("root_cause_file")
    root_cause_line = state.get("root_cause_line")
    root_cause_type = state.get("root_cause_type")
    root_cause_summary = state.get("root_cause_summary")


    prompt = f"""
    You are a senior backend engineer and SRE preparing a production-safe fix plan.

    Your job is to create a clear, minimal, low-risk remediation plan based only on the root cause details provided.

    ## Root Cause Details
    - Root cause file: {root_cause_file}
    - Root cause line: {root_cause_line}
    - Root cause type: {root_cause_type}
    - Root cause summary: {root_cause_summary}

    ## Planning Rules
    - Use only the root cause details provided above.
    - Do not invent code, files, classes, methods, services, owners, tickets, or PRs.
    - If the root cause file or line is missing, clearly say the fix location is unknown.
    - Prefer the smallest safe fix.
    - For production incidents, include both immediate mitigation and permanent fix.
    - If the root cause type is NullPointerException, prioritize null validation, defensive checks, safer defaults, and tests for missing/null fields.
    - If the issue started after deployment, include rollback as an immediate mitigation option.
    - Do not directly modify code.
    - Do not claim the fix is guaranteed.
    - Return ONLY valid JSON.
    - Do not include markdown.
    - Do not include explanations outside JSON.

    ## Your Task
    Create a fix plan with:
    1. Immediate mitigation
    2. Code fix plan
    3. Test plan
    4. Rollback plan
    5. Validation plan after fix
    6. Risk level
    7. Human approval checklist

    ## Required JSON Output Schema
    {{
    "fix_location": {{
        "file": "string or null",
        "line": "number or null"
    }},
    "immediate_mitigation": "string",
    "code_fix_plan": [
        "string"
    ],
    "test_plan": [
        "string"
    ],
    "rollback_plan": "string",
    "post_fix_validation": [
        "string"
    ],
    "risk_level": "low | medium | high",
    "requires_human_approval": true,
    "human_approval_checklist": [
        "string"
    ],
    "reasoning": "string"
    }}
    CRITICAL: Your response must start with {{ and end with }}.
        Do not use markdown.
        Do not use backticks.
        Do not use ```json.
        Return raw JSON only.
"""

    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens = 1000,
        messages = [
            {"role" : "user", "content" : prompt}
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
        
        result = json.loads(clean_response)
        return {
                "fix_plan": result,           
                "current_status": "fix_planned"
        }
    except json.JSONDecodeError:
        return {
            "root_cause_summary": response_text,
            "confidence_score":   0.3,
            "current_status":     "root_cause_found",
            "errors":             ["Failed to parse Claude response as JSON"]
        }