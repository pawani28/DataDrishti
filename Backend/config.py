import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# On Vercel, the filesystem is read-only except /tmp
if os.environ.get("VERCEL"):
    UPLOAD_DIR = Path("/tmp/uploads")
    DB_PATH = Path("/tmp/datadrishti.db")
else:
    UPLOAD_DIR = BASE_DIR / "uploads"
    DB_PATH = BASE_DIR / "datadrishti.db"

MAX_UPLOAD_MB = 25
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
