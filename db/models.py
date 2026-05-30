from sqlalchemy import (
    Column, String, Integer, Float,
    DateTime, JSON, Text, Boolean,
    ForeignKey, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class SeverityLevel(enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class IncidentStatus(enum.Enum):
    RECEIVED        = "received"
    INVESTIGATING   = "investigating"
    ROOT_CAUSE_FOUND= "root_cause_found"
    FIX_GENERATED   = "fix_generated"
    AWAITING_APPROVAL = "awaiting_approval"
    FIX_APPROVED    = "fix_approved"
    FIX_REJECTED    = "fix_rejected"
    PR_MERGED       = "pr_merged"
    CONFLUENCE_DRAFT= "confluence_draft"
    RESOLVED        = "resolved"
    ESCALATED       = "escalated"
    FAILED          = "failed"

class ApprovalStatus(enum.Enum):
    PENDING          = "pending"
    APPROVED         = "approved"
    REJECTED         = "rejected"
    ESCALATED        = "escalated"
    REQUEST_CHANGES  = "request_changes"
    TIMEOUT          = "timeout"

class Incident(Base):
    __tablename__ = "incidents"

    id               = Column(String, primary_key=True)
    alert_payload    = Column(JSON, nullable=False)
    severity         = Column(Enum(SeverityLevel), nullable=False)
    status           = Column(Enum(IncidentStatus), default=IncidentStatus.RECEIVED)
    environment      = Column(String, nullable=False)
    affected_service = Column(String, nullable=False)
    alert_timestamp  = Column(DateTime, nullable=False)

    log_evidence        = Column(JSON, nullable=True)
    metrics_evidence    = Column(JSON, nullable=True)
    trace_evidence      = Column(JSON, nullable=True)
    deployment_evidence = Column(JSON, nullable=True)

    suspected_service   = Column(String,  nullable=True)
    suspected_commit    = Column(String,  nullable=True)
    suspected_pr        = Column(String,  nullable=True)
    root_cause_summary  = Column(Text,    nullable=True)
    confidence_score    = Column(Float,   nullable=True)

    fix_plan        = Column(JSON,   nullable=True)
    branch_name     = Column(String, nullable=True)
    fix_pr_url      = Column(String, nullable=True)
    merge_status    = Column(String, nullable=True)

    confluence_url            = Column(String,  nullable=True)
    teams_notification_status = Column(String,  nullable=True)

    celery_task_id  = Column(String,  nullable=True)
    retry_count     = Column(Integer, default=0)
    errors          = Column(JSON,    nullable=True)

    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    event_type  = Column(String, nullable=False)
    node_name   = Column(String, nullable=True)
    message     = Column(Text,   nullable=False)
    data        = Column(JSON,   nullable=True)
    created_at  = Column(DateTime, server_default=func.now())


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    tool_name   = Column(String, nullable=False)
    mcp_server  = Column(String, nullable=False)
    input_data  = Column(JSON,   nullable=False) 
    output_data = Column(JSON,   nullable=True) 
    duration_ms = Column(Integer,nullable=True) 
    success     = Column(Boolean,default=True)
    error       = Column(Text,   nullable=True)
    created_at  = Column(DateTime, server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    incident_id   = Column(String, ForeignKey("incidents.id"), nullable=False)
    approval_type = Column(String, nullable=False) 
    status        = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    reviewer      = Column(String, nullable=True)
    notes         = Column(Text,   nullable=True) 
    teams_card_id = Column(String, nullable=True) 
    requested_at  = Column(DateTime, server_default=func.now())
    decided_at    = Column(DateTime, nullable=True)
    timeout_at    = Column(DateTime, nullable=True) 


class FixAttempt(Base):
    __tablename__ = "fix_attempts"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    incident_id   = Column(String, ForeignKey("incidents.id"), nullable=False)
    attempt_number= Column(Integer, nullable=False)
    fix_plan      = Column(JSON,    nullable=True)
    changed_files = Column(JSON,    nullable=True)
    patch         = Column(Text,    nullable=True)
    test_results  = Column(JSON,    nullable=True)
    success       = Column(Boolean, default=False)
    failure_reason= Column(Text,    nullable=True)
    created_at    = Column(DateTime, server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    incident_id     = Column(String, ForeignKey("incidents.id"), nullable=False)
    channel         = Column(String, nullable=False) 
    notification_type = Column(String, nullable=False) 
    message         = Column(Text,    nullable=False)
    status          = Column(String,  nullable=False)
    teams_message_id= Column(String,  nullable=True)
    error           = Column(Text,    nullable=True)
    sent_at         = Column(DateTime, server_default=func.now())