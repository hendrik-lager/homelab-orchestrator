from pydantic import BaseModel
from datetime import datetime

class JobBase(BaseModel):
    name: str
    job_type: str
    host_id: int | None = None
    cron_expression: str | None = None
    enabled: bool = True

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    name: str | None = None
    job_type: str | None = None
    host_id: int | None = None
    cron_expression: str | None = None
    enabled: bool | None = None

class JobResponse(JobBase):
    id: int
    last_run: datetime | None
    last_result: str | None
    next_run: datetime | None

    class Config:
        from_attributes = True
