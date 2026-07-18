import enum
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum, JSON
from sqlalchemy.orm import relationship

from .database import Base

def get_utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class ScheduleType(str, enum.Enum):
    specific_time = "specific_time"
    cron = "cron"
    interval = "interval"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    channels = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="owner", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="owner", cascade="all, delete-orphan")
    custom_variables = relationship("CustomVariable", back_populates="owner", cascade="all, delete-orphan")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plugin_id = Column(String, index=True)
    name = Column(String)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    owner = relationship("User", back_populates="channels")
    notifications = relationship("Notification", back_populates="channel", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    title = Column(String)
    payload = Column(Text)
    schedule_type = Column(Enum(ScheduleType))
    schedule_expr = Column(String)
    parameters = Column(JSON, default={})
    exclusions = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    next_run_at = Column(DateTime, nullable=True)
    start_time = Column(DateTime, nullable=True)
    execution_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    owner = relationship("User", back_populates="notifications")
    channel = relationship("Channel", back_populates="notifications")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    is_official = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plugin_id = Column(String, index=True)
    name = Column(String)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    owner = relationship("User", back_populates="data_sources")

class CustomVariable(Base):
    __tablename__ = "custom_variables"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    value = Column(String)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    owner = relationship("User", back_populates="custom_variables")
