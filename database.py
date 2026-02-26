"""
Database module for storing financial analysis results.

Uses SQLAlchemy with SQLite for lightweight, zero-configuration storage.
"""

import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# Database configuration — defaults to SQLite file in project root
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    """Model for storing financial document analysis results."""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, file='{self.file_name}', query='{self.query[:50]}...')>"


class JobStatus(Base):
    """Model for tracking async analysis job status (used by Celery worker)."""

    __tablename__ = "job_status"

    id = Column(String(36), primary_key=True)  # UUID
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    file_name = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<JobStatus(id='{self.id}', status='{self.status}')>"
