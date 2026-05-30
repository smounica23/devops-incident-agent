from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AlertPayload(BaseModel):
    alertName : str
    severity : str
    affected_service : str
    environment : str
    error_message : str
    timestamp : Optional[datetime] = None
    labels : Optional[dict] = None
    runbook_url : Optional[str] = None