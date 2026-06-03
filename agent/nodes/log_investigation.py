from agent.state import IncidentState
import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone

es = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200"))


def log_investigation(state: IncidentState) -> dict:

    affected_service = state.get("affected_service")
    alert_timestamp = parse_alert_timestamp(state.get("alert_timestamp"))
    start = alert_timestamp - timedelta(minutes=30)
    end = alert_timestamp + timedelta(minutes=30)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    try:
        results = es.search(
            index="incidents-logs-*",
            query={
                "bool": {
                    "must": [
                        {"term": {"service": affected_service}},
                        {"terms": {"level": ["ERROR", "WARN"]}},
                        {"range": {
                            "timestamp": {
                                "gte": start_str,
                                "lte": end_str
                            }
                        }}
                    ]
                }
            },
            size=100
        )

        hits = results["hits"]["hits"]
        total_errors = results["hits"]["total"]["value"]

        error_types = list(set([
            hit["_source"].get("error_type")
            for hit in hits
            if hit["_source"].get("error_type")
        ]))

        stack_traces = list(set([
            hit["_source"].get("stack_trace")
            for hit in hits
            if hit["_source"].get("stack_trace")
        ]))

        timestamps = [
            hit["_source"].get("timestamp")
            for hit in hits
            if hit["_source"].get("timestamp")
        ]
        first_occurrence = min(timestamps) if timestamps else None

        log_evidence = {
            "total_errors": total_errors,
            "error_types": error_types,
            "stack_traces": stack_traces[:3],
            "first_occurrence": first_occurrence,
            "sample_messages": [
                hit["_source"].get("message")
                for hit in hits[:5]
            ]
        }

        return {"log_evidence": log_evidence}

    except Exception as e:
        return {
            "log_evidence": {
                "total_errors": 0,
                "error_types": [],
                "stack_traces": [],
                "first_occurrence": None,
                "sample_messages": [],
                "error": str(e)
            }
        }


def parse_alert_timestamp(timestamp):
    if not timestamp:
        return datetime.now(timezone.utc)

    if isinstance(timestamp, datetime):
        return timestamp

    if isinstance(timestamp, str):
        timestamp = timestamp.replace("Z", "+00:00")
        return datetime.fromisoformat(timestamp)

    raise ValueError(f"Unsupported timestamp format: {timestamp}")