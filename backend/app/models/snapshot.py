from datetime import datetime
from sqlalchemy import DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    cpu_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    ram_used_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ram_total_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_used_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_total_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    load_1m: Mapped[float | None] = mapped_column(Float, nullable=True)
