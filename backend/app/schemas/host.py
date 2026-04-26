from pydantic import BaseModel
from datetime import datetime

class HostBase(BaseModel):
    name: str
    host_type: str
    address: str
    port: int | None = None
    enabled: bool = True

class HostCreate(HostBase):
    credential_value: str | None = None
    cred_type: str = "api_token"
    username: str | None = None

class HostUpdate(BaseModel):
    name: str | None = None
    host_type: str | None = None
    address: str | None = None
    port: int | None = None
    enabled: bool | None = None

class HostResponse(HostBase):
    id: int
    last_seen: datetime | None = None
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
