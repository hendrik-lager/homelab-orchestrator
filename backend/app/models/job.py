from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=True)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    next_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
