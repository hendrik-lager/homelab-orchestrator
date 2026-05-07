from pydantic import BaseModel
from datetime import datetime

class UpdateRecordResponse(BaseModel):
    id: int
    host_id: int
    host_name: str | None
    service_id: int | None
    update_type: str
    package_name: str | None
    current_version: str | None
    available_version: str | None
    is_security: bool
    severity: str
    cve_ids: str | None
    status: str
    detected_at: datetime
    applied_at: datetime | None
    notes: str | None

    class Config:
        from_attributes = True
