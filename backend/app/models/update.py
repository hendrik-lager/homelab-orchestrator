from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UpdateRecord(Base):
    __tablename__ = "update_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    update_type: Mapped[str] = mapped_column(String(50), nullable=False)
    package_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    current_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    available_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_security: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
