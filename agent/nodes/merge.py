from agent.state import IncidentState
from github import Github
import os
    
    
g = Github(os.getenv("GITHUB_TOKEN"))


def merge(state: IncidentState) -> dict:

    fix_pr_url = state.get("fix_pr_url")
    pr_number = int(fix_pr_url.split("/")[-1])
    repo = g.get_repo(f"{os.getenv('GITHUB_REPO_OWNER')}/{os.getenv('GITHUB_TARGET_REPO')}")
    pr = repo.get_pull(pr_number)
    pr.merge(merge_method="squash")
    return {
        "merge_status": "merged",
        "current_status": "pr_merged"
    }