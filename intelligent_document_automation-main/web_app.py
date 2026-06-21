"""Flask web frontend for the document automation pipeline."""

from __future__ import annotations

import logging
import shutil
import traceback
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from src.pipeline import run_pipeline
from src.api import api
from src.logger_config import setup_logging
from src.middleware.error_handler import register_error_handlers


BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / "web_runs"
ALLOWED_EXTENSIONS = {".pdf"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config["SECRET_KEY"] = "document-automation-demo"

# Register API blueprint
app.register_blueprint(api)

# Register error handlers
register_error_handlers(app)

# Setup logging
logger = setup_logging()


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def create_run_workspace() -> Path:
    run_id = uuid.uuid4().hex[:12]
    run_dir = RUNS_DIR / run_id
    (run_dir / "input_pdfs").mkdir(parents=True, exist_ok=True)
    return run_dir


def cleanup_previous_runs(keep_last: int = 5) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_dirs = sorted(
        [path for path in RUNS_DIR.iterdir() if path.is_dir()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old_run in run_dirs[keep_last:]:
        shutil.rmtree(old_run, ignore_errors=True)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    uploaded_files = []

    try:
        if request.method == "POST":
            files = request.files.getlist("pdf_files")
            valid_files = [file for file in files if file and file.filename and allowed_file(file.filename)]

            if not valid_files:
                error = "Please upload at least one PDF file."
                logger.warning("Upload attempt with no valid files")
            else:
                try:
                    run_dir = create_run_workspace()
                    input_dir = run_dir / "input_pdfs"

                    for uploaded in valid_files:
                        filename = secure_filename(uploaded.filename)
                        target = input_dir / filename
                        
                        # Check file size (max 25MB per file)
                        uploaded.seek(0, 2)  # Seek to end
                        file_size = uploaded.tell()
                        uploaded.seek(0)  # Seek back to beginning
                        
                        if file_size > 25 * 1024 * 1024:
                            error = f"File '{filename}' exceeds 25MB limit."
                            logger.error(f"File size exceeded: {filename} ({file_size} bytes)")
                            break
                        
                        try:
                            uploaded.save(target)
                            uploaded_files.append(filename)
                            logger.info(f"Successfully saved file: {filename}")
                        except Exception as save_error:
                            error = f"Failed to save file '{filename}': {str(save_error)}"
                            logger.error(f"File save error: {filename} - {save_error}")
                            break
                    
                    if error:
                        # Clean up the run directory if there was an error
                        shutil.rmtree(run_dir, ignore_errors=True)
                    else:
                        try:
                            result = run_pipeline(str(run_dir))
                            result["run_id"] = run_dir.name
                            result["uploaded_files"] = uploaded_files
                            result["output_items"] = [
                                {
                                    "filename": Path(file_path).name,
                                    "download_url": url_for("download_file", run_id=run_dir.name, filename=Path(file_path).name),
                                }
                                for file_path in result.get("output_files", [])
                            ]
                            
                            # Prepare detailed extraction results for display
                            extraction_details = []
                            if result.get("extracted_fields"):
                                for doc_name, fields in result["extracted_fields"].items():
                                    doc_extraction = {"name": doc_name, "fields": []}
                                    if isinstance(fields, dict):
                                        for field_name, field_data in fields.items():
                                            if isinstance(field_data, dict) and len(field_data) > 0 and field_data.get('confidence', 0) > 0:
                                                # Safe dict access: get first key safely
                                                first_key = list(field_data.keys())[0]
                                                field_value = field_data.get(first_key)
                                                if field_value is not None:
                                                    doc_extraction["fields"].append({
                                                        "name": field_name.replace('_', ' ').title(),
                                                        "value": field_value,
                                                        "confidence": field_data.get("confidence", 0)
                                                    })
                                    if doc_extraction["fields"]:
                                        extraction_details.append(doc_extraction)
                            result["extraction_details"] = extraction_details
                            
                            # Prepare classification details for display
                            classification_details = []
                            if result.get("classifications"):
                                for doc_name, classification in result["classifications"].items():
                                    if isinstance(classification, dict) and classification.get("confidence", 0) > 0:
                                        classification_details.append({
                                            "name": doc_name,
                                            "type": classification.get("document_type", "Unknown"),
                                            "confidence": classification.get("confidence", 0),
                                            "explanation": classification.get("explanation", "")
                                        })
                            result["classification_details"] = classification_details

                            cleanup_previous_runs()
                            logger.info(f"Pipeline completed successfully for run {run_dir.name}")
                            
                        except Exception as pipeline_error:
                            error = f"Pipeline execution failed: {str(pipeline_error)}"
                            logger.error(f"Pipeline error: {pipeline_error}\n{traceback.format_exc()}")
                            # Clean up the run directory if pipeline failed
                            shutil.rmtree(run_dir, ignore_errors=True)
                            
                except Exception as workspace_error:
                    error = f"Failed to create workspace: {str(workspace_error)}"
                    logger.error(f"Workspace creation error: {workspace_error}\n{traceback.format_exc()}")
                    
    except RequestEntityTooLarge:
        error = "Total upload size exceeds 25MB limit. Please upload smaller files."
        logger.warning("Request entity too large")
    except Exception as e:
        error = f"An unexpected error occurred: {str(e)}"
        logger.error(f"Unexpected error in index route: {e}\n{traceback.format_exc()}")

    return render_template(
        "index.html",
        result=result,
        error=error,
        uploaded_files=uploaded_files,
    )


@app.route("/download/<run_id>/<path:filename>")
def download_file(run_id: str, filename: str):
    try:
        # Validate and sanitize filename to prevent path traversal attacks
        filename = secure_filename(filename)
        if not filename:
            logger.warning(f"Invalid filename attempt: {filename}")
            return jsonify({"error": "Invalid filename"}), 400
        
        run_dir = RUNS_DIR / run_id / "output"
        
        # Check if the file exists
        file_path = run_dir / filename
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        logger.info(f"Downloading file: {filename} from run {run_id}")
        return send_from_directory(run_dir, filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Download error for {filename}: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}\n{traceback.format_exc()}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(RequestEntityTooLarge)
def request_entity_too_large(error):
    logger.warning(f"File upload too large: {error}")
    return jsonify({"error": "File upload exceeds 25MB limit"}), 413

if __name__ == "__main__":
    try:
        cleanup_previous_runs()
        logger.info("Starting Flask web application")
        app.run(host="127.0.0.1", port=5000, debug=False)
    except Exception as e:
        logger.error(f"Failed to start application: {e}\n{traceback.format_exc()}")
        raise
        raise
