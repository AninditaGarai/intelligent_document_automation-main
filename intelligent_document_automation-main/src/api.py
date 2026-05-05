"""
REST API layer for the document processing pipeline.

Provides endpoints for:
- Submitting PDF batches for processing
- Polling job status
- Retrieving results
- Health checks
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict

from flask import Blueprint, request, jsonify

from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix="/api/v1")

# In-memory job tracker (in production, use a database)
JOBS: Dict[str, Dict[str, Any]] = {}


@api.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "1.0.0"})


@api.route("/submit", methods=["POST"])
def submit_job():
    """
    Submit a batch of PDF files for processing.
    
    Returns: job_id for polling status
    """
    files = request.files.getlist("files")
    
    if not files:
        return jsonify({"error": "No files provided"}), 400
    
    job_id = str(uuid.uuid4())[:12]
    workspace_dir = Path("api_runs") / job_id
    input_dir = workspace_dir / "input_pdfs"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    filenames = []
    for file in files:
        if file and file.filename:
            filename = Path(file.filename).name
            file.save(input_dir / filename)
            filenames.append(filename)
    
    # Store job metadata
    JOBS[job_id] = {
        "status": "submitted",
        "files": filenames,
        "workspace": str(workspace_dir),
        "result": None,
    }
    
    logger.info(f"Job {job_id} submitted with {len(filenames)} files")
    
    return jsonify({"job_id": job_id, "files_received": len(filenames)}), 202


@api.route("/jobs/<job_id>/status", methods=["GET"])
def get_status(job_id: str):
    """Get the status of a submitted job."""
    if job_id not in JOBS:
        return jsonify({"error": "Job not found"}), 404
    
    job = JOBS[job_id]
    return jsonify({
        "job_id": job_id,
        "status": job["status"],
        "files": job["files"],
    })


@api.route("/jobs/<job_id>/process", methods=["POST"])
def process_job(job_id: str):
    """Trigger processing for a submitted job."""
    if job_id not in JOBS:
        return jsonify({"error": "Job not found"}), 404
    
    job = JOBS[job_id]
    if job["status"] != "submitted":
        return jsonify({"error": "Job already processed or in progress"}), 400
    
    job["status"] = "processing"
    
    try:
        workspace_dir = job["workspace"]
        result = run_pipeline(workspace_dir)
        
        job["status"] = "completed" if result["status"] == "ok" else "failed"
        job["result"] = result
        
        logger.info(f"Job {job_id} completed with status {result['status']}")
        
        return jsonify({
            "job_id": job_id,
            "status": job["status"],
            "summary": result.get("summary"),
            "output_files": [Path(f).name for f in result.get("output_files", [])],
        }), 200
    
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        logger.error(f"Job {job_id} failed: {e}")
        return jsonify({"error": str(e)}), 500


@api.route("/jobs/<job_id>/results", methods=["GET"])
def get_results(job_id: str):
    """Get processing results for a completed job."""
    if job_id not in JOBS:
        return jsonify({"error": "Job not found"}), 404
    
    job = JOBS[job_id]
    if job["status"] != "completed":
        return jsonify({"error": f"Job status is {job['status']}, not completed"}), 400
    
    result = job.get("result", {})
    return jsonify({
        "job_id": job_id,
        "summary": result.get("summary"),
        "output_files": [Path(f).name for f in result.get("output_files", [])],
    })


@api.route("/jobs", methods=["GET"])
def list_jobs():
    """List all jobs and their statuses."""
    jobs_list = [
        {"job_id": jid, "status": job["status"], "files": len(job["files"])}
        for jid, job in JOBS.items()
    ]
    return jsonify({"jobs": jobs_list, "total": len(jobs_list)})
