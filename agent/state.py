from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class IncidentState(TypedDict):
    incident_id : str
    alert_payload : dict
    severity : str
    environment : str
    affected_service : str
    alert_timestamp : str


    log_evidence :  Optional[dict]
    metrics_evidence :  Optional[dict]
    trace_evidence :  Optional[dict]
    deployment_evidence :  Optional[dict]

    suspected_service : Optional[str]
    suspected_commit : Optional[str]
    suspected_pr : Optional[str]
    root_cause_summary : Optional[str]
    confidence_score : Optional[float]
    root_cause_file   : Optional[str]
    root_cause_line   : Optional[int]
    root_cause_type   : Optional[str]
    fix_hint          : Optional[str]


    fix_plan :  Optional[dict]
    branch_name : Optional[str]
    fix_pr_url : Optional[str]
    merge_status : Optional[str]
    approval_status : Optional[str]


    confluence_url : Optional[str]
    teams_notification_status : Optional[str]

    messages : Annotated[list[BaseMessage], add_messages]
    current_status : Optional[str]
    retry_count : int
    errors : Optional[list]