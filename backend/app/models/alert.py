from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="SET NULL"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="firing")
    fired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
