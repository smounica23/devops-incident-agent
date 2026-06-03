from agent.state import IncidentState

def deployment_investigation(state: IncidentState) -> dict:

    deployment_evidence = {
        "service":           "payment-service",
        "deployment_time":   "2026-06-03T14:15:00Z",
        "commit_sha":        "abc123def456",
        "image_tag":         "payment-service:2.1.4",
        "deployed_by":       "github-actions",
        "deployment_tool":   "ArgoCD",
        "environment":       "production",
        "previous_version":  "2.1.3",
        "previous_commit":   "xyz789abc123",
        "time_diff_minutes": 7,
        "data_source":       "mock_argocd"
    }

    return {"deployment_evidence": deployment_evidence}