"""
SQLAlchemy models for database tables.
These models define the schema for the TimescaleDB tables.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    preferences = Column(JSON)
    created_at = Column(DateTime, server_default="now()")

    study_sessions = relationship("StudySession", back_populates="user")


class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, server_default="now()")
    end_time = Column(DateTime)
    topics = Column(JSON)

    user = relationship("User", back_populates="study_sessions")
    queries = relationship("QueryLog", back_populates="session")


class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("study_sessions.id"), nullable=False
    )
    query = Column(String, nullable=False)
    response = Column(String)
    agent_id = Column(String)
    processing_time = Column(Float)
    timestamp = Column(DateTime, server_default="now()")

    session = relationship("StudySession", back_populates="queries")


class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default="now()")
    updated_at = Column(DateTime, server_default="now()", onupdate="now()")

    # You could add relationships to verses or topics here later
    # user = relationship("User", back_populates="notes")
