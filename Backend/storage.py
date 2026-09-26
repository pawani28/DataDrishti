import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "datadrishti.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                rows INTEGER NOT NULL DEFAULT 0,
                columns INTEGER NOT NULL DEFAULT 0,
                uploaded_at TEXT NOT NULL
            )
        """)
        conn.commit()

def add_dataset(filename, stored_path, rows, columns):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO datasets(filename, stored_path, rows, columns, uploaded_at) VALUES (?, ?, ?, ?, ?)",
            (filename, stored_path, rows, columns, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return cur.lastrowid

def get_dataset(dataset_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,)).fetchone()

def latest_dataset():
    with connect() as conn:
        return conn.execute("SELECT * FROM datasets ORDER BY id DESC LIMIT 1").fetchone()
