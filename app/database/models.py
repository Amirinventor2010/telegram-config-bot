from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
    Boolean,
    Text,
)
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    pass


# =========================
# 👤 Users
# =========================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False
    )

    # 🔴 سیستم بن
    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False
    )

    # آیا تبلیغات اولیه را دیده؟
    ads_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# =========================
# 👑 Admins
# =========================
class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


# =========================
# 📦 Configs / Proxies
# =========================
class Config(Base):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(
        String(50),  # v2ray / npv / proxy
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


# =========================
# 📢 Advertisement Channels
# =========================
class AdChannel(Base):
    __tablename__ = "ad_channels"

    id: Mapped[int] = mapped_column(primary_key=True)

    channel_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    invite_link: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    ad_type: Mapped[str] = mapped_column(
        String(20),  # join / view
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
