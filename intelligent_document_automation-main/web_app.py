"""Flask web frontend for the document automation pipeline."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from src.pipeline import run_pipeline


BASE_DIR = Path(__file__).resolve().parent
RUNS_DIR = BASE_DIR / "web_runs"
ALLOWED_EXTENSIONS = {".pdf"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
app.config["SECRET_KEY"] = "document-automation-demo"


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

    if request.method == "POST":
        files = request.files.getlist("pdf_files")
        valid_files = [file for file in files if file and file.filename and allowed_file(file.filename)]

        if not valid_files:
            error = "Please upload at least one PDF file."
        else:
            run_dir = create_run_workspace()
            input_dir = run_dir / "input_pdfs"

            for uploaded in valid_files:
                filename = secure_filename(uploaded.filename)
                target = input_dir / filename
                uploaded.save(target)
                uploaded_files.append(filename)

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

            cleanup_previous_runs()

    return render_template(
        "index.html",
        result=result,
        error=error,
        uploaded_files=uploaded_files,
    )


@app.route("/download/<run_id>/<path:filename>")
def download_file(run_id: str, filename: str):
    run_dir = RUNS_DIR / run_id / "output"
    return send_from_directory(run_dir, filename, as_attachment=True)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    cleanup_previous_runs()
    app.run(host="127.0.0.1", port=5000, debug=True)
