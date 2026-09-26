from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from Backend.config import UPLOAD_DIR, MAX_UPLOAD_MB, ALLOWED_EXTENSIONS
from Backend.analytics import load_dataframe, clean_dataframe, summarize, dashboard_data, insights, answer_question
from Backend.storage import init_db, add_dataset, get_dataset, latest_dataset

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "html"

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

UPLOAD_DIR.mkdir(exist_ok=True)
init_db()

def json_error(message, status=400):
    return jsonify({"success": False, "error": message}), status

@app.get("/api/health")
def health():
    return jsonify({"success": True, "service": "DataDrishti API"})

@app.post("/api/upload")
def upload_dataset():
    if "file" not in request.files:
        return json_error("No file provided.")

    file = request.files["file"]
    if not file.filename:
        return json_error("Please select a file.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return json_error("Only CSV, XLSX and XLS files are supported.")

    safe_name = secure_filename(file.filename)
    stored_name = f"{uuid4().hex}_{safe_name}"
    path = UPLOAD_DIR / stored_name
    file.save(path)

    try:
        df = clean_dataframe(load_dataframe(path))
        dataset_id = add_dataset(safe_name, str(path), len(df), len(df.columns))
        return jsonify({
            "success": True,
            "dataset_id": dataset_id,
            "filename": safe_name,
            "summary": summarize(df),
            "dashboard": dashboard_data(df),
            "insights": insights(df)
        }), 201
    except Exception as exc:
        path.unlink(missing_ok=True)
        return json_error(f"Could not process dataset: {exc}", 422)

def get_df(dataset_id):
    row = get_dataset(dataset_id)
    if not row:
        return None, json_error("Dataset not found.", 404)
    return clean_dataframe(load_dataframe(Path(row["stored_path"]))), None

@app.get("/api/datasets/<int:dataset_id>")
def dataset_summary(dataset_id):
    df, error = get_df(dataset_id)
    if error:
        return error
    return jsonify({"success": True, "summary": summarize(df), "insights": insights(df)})

@app.get("/api/datasets/<int:dataset_id>/dashboard")
def dataset_dashboard(dataset_id):
    df, error = get_df(dataset_id)
    if error:
        return error
    return jsonify({"success": True, "dashboard": dashboard_data(df), "insights": insights(df)})

@app.post("/api/datasets/<int:dataset_id>/chat")
def dataset_chat(dataset_id):
    df, error = get_df(dataset_id)
    if error:
        return error
    body = request.get_json(silent=True) or {}
    question = str(body.get("question", "")).strip()
    if not question:
        return json_error("Question is required.")
    return jsonify({"success": True, "answer": answer_question(df, question)})

@app.get("/api/datasets/latest")
def latest():
    row = latest_dataset()
    if not row:
        return json_error("No dataset uploaded yet.", 404)
    df = clean_dataframe(load_dataframe(Path(row["stored_path"])))
    return jsonify({
        "success": True,
        "dataset": {
            "id": row["id"],
            "filename": row["filename"],
            "rows": row["rows"],
            "columns": row["columns"],
            "uploaded_at": row["uploaded_at"]
        },
        "dashboard": dashboard_data(df),
        "summary": summarize(df),
        "insights": insights(df)
    })

@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/<path:path>")
def frontend(path):
    target = FRONTEND_DIR / path
    if target.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.errorhandler(413)
def too_large(_):
    return json_error(f"File too large. Maximum size is {MAX_UPLOAD_MB} MB.", 413)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
