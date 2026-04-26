from pydantic import BaseModel
from datetime import datetime

class AlertResponse(BaseModel):
    id: int
    host_id: int | None
    service_id: int | None
    alert_type: str
    severity: str
    title: str
    body: str | None
    status: str
    fired_at: datetime
    resolved_at: datetime | None
    notification_sent: bool

    class Config:
        from_attributes = True

class AlertRuleCreate(BaseModel):
    name: str
    rule_type: str
    host_id: int | None = None
    threshold_value: float | None = None
    enabled: bool = True
    notify_email: bool = True

class AlertRuleResponse(AlertRuleCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
