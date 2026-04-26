from pydantic import BaseModel
from datetime import datetime

class ServiceBase(BaseModel):
    host_id: int
    name: str
    service_type: str
    external_id: str | None = None
    image: str | None = None
    status: str = "unknown"
    labels: str | None = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: str | None = None
    service_type: str | None = None
    external_id: str | None = None
    image: str | None = None
    status: str | None = None
    labels: str | None = None

class ServiceResponse(ServiceBase):
    id: int
    started_at: datetime | None = None
    last_checked: datetime | None = None

    class Config:
        from_attributes = True
