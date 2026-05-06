from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AutoUpdateSettings(Base):
    __tablename__ = "auto_update_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    security_only: Mapped[bool] = mapped_column(Boolean, default=True)
    # Standard-5-Feld Cron: minute hour day month weekday
    cron_expression: Mapped[str] = mapped_column(String(100), default="0 3 * * *")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
