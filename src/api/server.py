"""
FastAPI server for the BCP Calculator API.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import os
import uuid

from .models import StoryRequest, JobStatus
from ..bcp import BCPCalculator, setup_logger

# In-memory job storage (replace with database for production)
jobs = {}

app = FastAPI(
    title="BCP Calculator API",
    description="API for calculating Business Complexity Points (BCP) of user stories",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Root endpoint returning API information."""
    return {
        "name": "BCP Calculator API",
        "version": "1.0.0",
        "description": "API for calculating Business Complexity Points (BCP) of user stories"
    }


@app.post("/calculate", response_model=Dict[str, str])
def calculate_bcp(story: StoryRequest, background_tasks: BackgroundTasks):
    """Start BCP calculation job."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "result": None}
    
    background_tasks.add_task(
        process_bcp_calculation, 
        job_id=job_id,
        story_content=story.content,
        provider=story.provider
    )
    
    return {"job_id": job_id}


@app.get("/status/{job_id}", response_model=JobStatus)
def get_status(job_id: str):
    """Get job status and results if complete."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "result": jobs[job_id].get("result"),
        "error": jobs[job_id].get("error")
    }


def process_bcp_calculation(job_id: str, story_content: str, provider: str):
    """Process BCP calculation in background."""
    logger = setup_logger(logging.INFO)
    
    try:
        # Update status to processing
        jobs[job_id]["status"] = "processing"
        
        # Calculate BCP
        calculator = BCPCalculator(logger, provider_name=provider)
        result = calculator.calculate_bcp(story_content)
        
        # Update job with results
        jobs[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        logger.error(f"Error calculating BCP: {str(e)}")
        jobs[job_id] = {"status": "failed", "error": str(e)}