from agent.state import IncidentState
from anthropic import Anthropic
from github import Github
import os
import json

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
g = Github(os.getenv("GITHUB_TOKEN"))

def code_fix(state: IncidentState) -> dict:

    fix_plan = state.get("fix_plan", {})
    root_cause_file = state.get("root_cause_file")
    repo = g.get_repo(f"{os.getenv('GITHUB_REPO_OWNER')}/{os.getenv('GITHUB_TARGET_REPO')}")
    file_path = "src/main/java/com/company/payment/PaymentValidator.java"
    file_content = repo.get_contents(file_path)
    current_code = file_content.decoded_content.decode("utf-8")

    prompt = f"""
You are a senior Java engineer fixing a production bug.

## Current buggy code:
{current_code}

## Fix plan:
{json.dumps(fix_plan, indent=2)}

## Your task:
Apply the fix plan to the buggy code.
Return ONLY the complete fixed Java file content.
No explanations. No markdown. Just the raw Java code.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    fixed_code = response.content[0].text.strip()

    if fixed_code.startswith("```java"):
        fixed_code = fixed_code[7:]
    if fixed_code.startswith("```"):
        fixed_code = fixed_code[3:]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code[:-3]
    fixed_code = fixed_code.strip()
    return {
        "changed_files": {
            file_path: fixed_code
        },
        "current_status": "fix_generated"
    }