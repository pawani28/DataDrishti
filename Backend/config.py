from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "datadrishti.db"

MAX_UPLOAD_MB = 25
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
