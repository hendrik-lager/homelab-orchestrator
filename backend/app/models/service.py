from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_checked: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    labels: Mapped[str | None] = mapped_column(Text, nullable=True)

    host: Mapped["Host"] = relationship(back_populates="services")
    checks: Mapped[list["ServiceCheck"]] = relationship(back_populates="service", cascade="all, delete-orphan")

class ServiceCheck(Base):
    __tablename__ = "service_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    service: Mapped["Service"] = relationship(back_populates="checks")
