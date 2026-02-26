import os
import uuid

from fastapi import FastAPI, File, UploadFile, Form, HTTPException


from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document,
    investment_analysis,
    risk_assessment,
    verification,
)
from database import SessionLocal, engine, Base, AnalysisResult, JobStatus

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI agents for comprehensive investment insights.",
    version="1.0.0",
)


def run_crew(query: str, file_path: str = "data/sample.pdf") -> str:
    """Run the full financial analysis crew pipeline.

    Args:
        query: The user's analysis query.
        file_path: Path to the uploaded financial document PDF.

    Returns:
        str: The comprehensive analysis result from the crew.
    """
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
        verbose=True,
    )

    result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Synchronous — upload and analyze a financial document",
            "POST /analyze/async": "Asynchronous — submit analysis job to queue",
            "GET /status/{job_id}": "Check async job status",
            "GET /results": "List all past analysis results",
            "GET /results/{result_id}": "Get a specific analysis result",
        },
    }


@app.post("/analyze")
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    """Analyze a financial document synchronously.

    - Upload a PDF financial document
    - Optionally provide a specific analysis query
    - Returns AI-powered analysis with investment insights, risk assessment, and recommendations
    - Note: This is a blocking call. For large documents, consider using /analyze/async instead.
    """

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)

        analysis_text = str(response)

        # Save result to database
        db = SessionLocal()
        try:
            db_result = AnalysisResult(
                file_name=file.filename,
                query=query.strip(),
                analysis=analysis_text,
            )
            db.add(db_result)
            db.commit()
            db.refresh(db_result)
            result_id = db_result.id
        finally:
            db.close()

        return {
            "status": "success",
            "result_id": result_id,
            "query": query,
            "analysis": analysis_text,
            "file_processed": file.filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}",
        )

    finally:
        # Clean up uploaded file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


@app.post("/analyze/async")
async def analyze_document_async(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    """Submit a financial document for asynchronous analysis via the job queue.

    - Upload a PDF financial document
    - Optionally provide a specific analysis query
    - Returns a job_id immediately — use GET /status/{job_id} to track progress
    - Requires Redis and Celery worker to be running
    """

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    job_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{job_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"

        # Create job record in database
        db = SessionLocal()
        try:
            job = JobStatus(
                id=job_id,
                status="pending",
                file_name=file.filename,
                query=query.strip(),
            )
            db.add(job)
            db.commit()
        finally:
            db.close()

        # Submit to Celery queue
        from worker import analyze_document_task

        analyze_document_task.delay(
            job_id=job_id,
            query=query.strip(),
            file_path=file_path,
            file_name=file.filename,
        )

        return {
            "status": "accepted",
            "job_id": job_id,
            "message": "Analysis job submitted. Use GET /status/{job_id} to track progress.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting analysis job: {str(e)}",
        )


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of an async analysis job."""
    db = SessionLocal()
    try:
        job = db.query(JobStatus).filter(JobStatus.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found.")

        response = {
            "job_id": job.id,
            "status": job.status,
            "file_name": job.file_name,
            "query": job.query,
            "created_at": job.created_at.isoformat(),
        }

        if job.status == "completed":
            response["completed_at"] = job.completed_at.isoformat() if job.completed_at else None
            response["result"] = job.result

        if job.status == "failed":
            response["completed_at"] = job.completed_at.isoformat() if job.completed_at else None
            response["error"] = job.error

        return response
    finally:
        db.close()


@app.get("/results")
async def list_results():
    """List all past analysis results."""
    db = SessionLocal()
    try:
        results = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
        return {
            "status": "success",
            "count": len(results),
            "results": [
                {
                    "id": r.id,
                    "file_name": r.file_name,
                    "query": r.query,
                    "created_at": r.created_at.isoformat(),
                    "analysis_preview": (r.analysis[:200] + "...") if len(r.analysis) > 200 else r.analysis,
                }
                for r in results
            ],
        }
    finally:
        db.close()


@app.get("/results/{result_id}")
async def get_result(result_id: int):
    """Get a specific analysis result by ID."""
    db = SessionLocal()
    try:
        result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
        if not result:
            raise HTTPException(status_code=404, detail=f"Analysis result with ID {result_id} not found.")
        return {
            "status": "success",
            "result": {
                "id": result.id,
                "file_name": result.file_name,
                "query": result.query,
                "analysis": result.analysis,
                "created_at": result.created_at.isoformat(),
            },
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)