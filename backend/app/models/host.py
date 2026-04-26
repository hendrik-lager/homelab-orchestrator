from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host_type: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    credentials: Mapped[list["HostCredential"]] = relationship(back_populates="host", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="host", cascade="all, delete-orphan")

class HostCredential(Base):
    __tablename__ = "host_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    cred_type: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_value: Mapped[str] = mapped_column(String(4096), nullable=False)
    key_fingerprint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    host: Mapped["Host"] = relationship(back_populates="credentials")
