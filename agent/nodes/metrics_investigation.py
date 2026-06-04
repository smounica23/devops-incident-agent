from agent.state import IncidentState

def metrics_investigation(state: IncidentState) -> dict:

    metrics_evidence = {
        "error_rate_percent": 45.3,
        "error_rate_before_deploy": 0.1,
        "p95_response_time_ms": 4800,
        "p95_before_deploy_ms": 120,
        "request_rate_per_min": 450,
        "cpu_usage_percent": 78,
        "memory_usage_percent": 65,
        "exception_rate_per_min": 47,
        "npe_count_by_endpoint": {
            "/api/v1/payments": 142
        },
        "data_source": "mock_prometheus"
    }
    return {"metrics_evidence": metrics_evidence}