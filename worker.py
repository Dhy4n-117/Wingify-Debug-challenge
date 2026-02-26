"""
Celery worker for handling concurrent financial document analysis requests.

This module implements the Queue Worker Model using Celery with Redis as the message broker.
It enables asynchronous processing of financial documents, allowing the API to handle
multiple concurrent requests without blocking.

Setup:
    1. Install and start Redis: https://redis.io/download
    2. Start the Celery worker:
       celery -A worker worker --loglevel=info --pool=solo
    3. Use the /analyze/async endpoint to submit jobs
    4. Check status with /status/{job_id}
"""

import os
import uuid
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
    verification,
)
from database import SessionLocal, engine, Base, JobStatus, AnalysisResult

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Configure Celery with Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
)


@celery_app.task(bind=True, name="analyze_document_task")
def analyze_document_task(self, job_id: str, query: str, file_path: str, file_name: str):
    """Celery task to process financial document analysis asynchronously.

    Args:
        job_id: Unique identifier for this analysis job.
        query: The user's analysis query.
        file_path: Path to the uploaded PDF file.
        file_name: Original filename of the uploaded document.
    """
    db = SessionLocal()

    try:
        # Update job status to processing
        job = db.query(JobStatus).filter(JobStatus.id == job_id).first()
        if job:
            job.status = "processing"
            db.commit()

        # Run the CrewAI pipeline
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
            tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
            process=Process.sequential,
            verbose=True,
        )

        result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
        analysis_text = str(result)

        # Save analysis result
        analysis_result = AnalysisResult(
            file_name=file_name,
            query=query,
            analysis=analysis_text,
        )
        db.add(analysis_result)

        # Update job status to completed
        if job:
            job.status = "completed"
            job.result = analysis_text
            job.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "completed",
            "job_id": job_id,
            "analysis": analysis_text,
        }

    except Exception as e:
        # Update job status to failed
        if job:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        raise

    finally:
        db.close()

        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
