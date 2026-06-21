"""
REST API layer for the document processing pipeline.

This module provides a RESTful API for document processing operations.

Endpoints:
- GET  /api/v1/health - Health check endpoint
- POST /api/v1/submit - Submit PDF files for processing
- GET  /api/v1/jobs/<job_id>/status - Get job status
- POST /api/v1/jobs/<job_id>/process - Trigger job processing
- GET  /api/v1/jobs/<job_id>/results - Get job results
- GET  /api/v1/jobs - List all jobs

Authentication: None (public API)
Rate Limiting: Not implemented (add for production)
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix="/api/v1")

# In-memory job tracker with thread safety (in production, use a database)
JOBS: Dict[str, Dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()  # Thread-safe access to JOBS dict


def create_response(success: bool, data: Any = None, message: str = None, 
                    status_code: int = 200, error_code: str = None) -> tuple:
    """
    Create a consistent API response format.
    
    Args:
        success: Whether the request was successful
        data: Response data
        message: Response message
        status_code: HTTP status code
        error_code: Error code for failures
        
    Returns:
        Tuple of (json_response, status_code)
    """
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": data if data is not None else {}
    }
    
    if message:
        response["message"] = message
    
    if not success and error_code:
        response["error_code"] = error_code
    
    return jsonify(response), status_code


@api.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status and version
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "status": "ok",
                "version": "1.0.0"
            }
        }
    """
    return create_response(
        success=True,
        data={"status": "ok", "version": "1.0.0"},
        message="Service is healthy"
    )


@api.route("/submit", methods=["POST"])
def submit_job():
    """
    Submit a batch of PDF files for processing.
    
    Request:
        multipart/form-data with 'files' field containing PDF files
        
    Returns:
        JSON response with job_id for polling status
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "job_id": "string",
                "files_received": int
            },
            "message": "Job submitted successfully"
        }
        
    Error Response:
        {
            "success": false,
            "timestamp": "ISO-8601 timestamp",
            "message": "Error message",
            "error_code": "NO_FILES"
        }
    """
    files = request.files.getlist("files")
    
    if not files:
        return create_response(
            success=False,
            message="No files provided",
            status_code=400,
            error_code="NO_FILES"
        )
    
    job_id = str(uuid.uuid4())[:12]
    workspace_dir = Path("api_runs") / job_id
    input_dir = workspace_dir / "input_pdfs"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    filenames = []
    for file in files:
        if file and file.filename:
            # Validate file size (not empty)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            if file_size == 0:
                logger.warning(f"Empty file rejected: {file.filename}")
                continue
            file.seek(0)  # Reset to beginning
            
            # Sanitize filename to prevent path traversal
            filename = secure_filename(Path(file.filename).name)
            if not filename:
                logger.warning(f"Invalid filename rejected: {file.filename}")
                continue
                
            file.save(input_dir / filename)
            filenames.append(filename)
    
    # Store job metadata (thread-safe)
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "submitted",
            "files": filenames,
            "workspace": str(workspace_dir),
            "result": None,
        }
    
    logger.info(f"Job {job_id} submitted with {len(filenames)} files")
    
    return create_response(
        success=True,
        data={"job_id": job_id, "files_received": len(filenames)},
        message="Job submitted successfully",
        status_code=202
    )


@api.route("/jobs/<job_id>/status", methods=["GET"])
def get_status(job_id: str):
    """
    Get the status of a submitted job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        JSON response with job status information
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "job_id": "string",
                "status": "submitted|processing|completed|failed",
                "files": ["string"]
            }
        }
        
    Error Response:
        {
            "success": false,
            "timestamp": "ISO-8601 timestamp",
            "message": "Job not found",
            "error_code": "JOB_NOT_FOUND"
        }
    """
    with JOBS_LOCK:
        if job_id not in JOBS:
            return create_response(
                success=False,
                message="Job not found",
                status_code=404,
                error_code="JOB_NOT_FOUND"
            )
        
        job = JOBS[job_id]
        status_data = {
            "job_id": job_id,
            "status": job["status"],
            "files": job["files"],
        }
    
    return create_response(success=True, data=status_data)


@api.route("/jobs/<job_id>/process", methods=["POST"])
def process_job(job_id: str):
    """
    Trigger processing for a submitted job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        JSON response with processing results
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "job_id": "string",
                "status": "completed|failed",
                "summary": {
                    "documents_processed": int,
                    "document_types_identified": int,
                    "fields_extracted": int,
                    "document_pairs_matched": int
                },
                "output_files": ["string"]
            }
        }
        
    Error Response:
        {
            "success": false,
            "timestamp": "ISO-8601 timestamp",
            "message": "Error message",
            "error_code": "ERROR_CODE"
        }
    """
    try:
        with JOBS_LOCK:
            if job_id not in JOBS:
                return create_response(
                    success=False,
                    message="Job not found",
                    status_code=404,
                    error_code="JOB_NOT_FOUND"
                )
            
            job = JOBS[job_id]
            if job["status"] != "submitted":
                return create_response(
                    success=False,
                    message="Job already processed or in progress",
                    status_code=400,
                    error_code="JOB_ALREADY_PROCESSED"
                )
            
            job["status"] = "processing"
        
        result = run_pipeline(str(workspace_dir))
        
        with JOBS_LOCK:
            job["status"] = "completed" if result["status"] == "ok" else "failed"
            job["result"] = result
        
        logger.info(f"Job {job_id} completed with status {result['status']}")
        
        return create_response(
            success=True,
            data={
                "job_id": job_id,
                "status": job["status"],
                "summary": result.get("summary"),
                "output_files": [Path(f).name for f in result.get("output_files", [])],
            }
        )
    
    except Exception as e:
        with JOBS_LOCK:
            job["status"] = "failed"
            job["error"] = str(e)
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        return create_response(
            success=False,
            message=str(e),
            status_code=500,
            error_code="PROCESSING_ERROR"
        )


@api.route("/jobs/<job_id>/results", methods=["GET"])
def get_results(job_id: str):
    """
    Get processing results for a completed job.
    
    Args:
        job_id: Unique identifier for the job
        
    Returns:
        JSON response with detailed processing results
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "job_id": "string",
                "summary": {
                    "documents_processed": int,
                    "document_types_identified": int,
                    "fields_extracted": int,
                    "document_pairs_matched": int
                },
                "output_files": ["string"]
            }
        }
        
    Error Response:
        {
            "success": false,
            "timestamp": "ISO-8601 timestamp",
            "message": "Error message",
            "error_code": "ERROR_CODE"
        }
    """
    with JOBS_LOCK:
        if job_id not in JOBS:
            return create_response(
                success=False,
                message="Job not found",
                status_code=404,
                error_code="JOB_NOT_FOUND"
            )
        
        job = JOBS[job_id]
        if job["status"] != "completed":
            return create_response(
                success=False,
                message=f"Job status is {job['status']}, not completed",
                status_code=400,
                error_code="JOB_NOT_COMPLETED"
            )
        
        result = job.get("result", {})
        results_data = {
            "job_id": job_id,
            "summary": result.get("summary"),
            "output_files": [Path(f).name for f in result.get("output_files", [])],
        }
    
    return create_response(success=True, data=results_data)


@api.route("/jobs", methods=["GET"])
def list_jobs():
    """
    List all jobs and their statuses.
    
    Returns:
        JSON response with list of all jobs
        
    Response:
        {
            "success": true,
            "timestamp": "ISO-8601 timestamp",
            "data": {
                "jobs": [
                    {
                        "job_id": "string",
                        "status": "submitted|processing|completed|failed",
                        "files": int
                    }
                ],
                "total": int
            }
        }
    """
    jobs_list = [
        {"job_id": jid, "status": job["status"], "files": len(job["files"])}
        for jid, job in JOBS.items()
    ]
    return create_response(
        success=True,
        data={"jobs": jobs_list, "total": len(jobs_list)}
    )
