import sqlite3
from datetime import datetime
from Backend.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                rows INTEGER NOT NULL,
                columns INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL
            )
        """)
        conn.commit()

def add_dataset(filename: str, stored_path: str, rows: int, columns: int) -> int:
    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO datasets (filename, stored_path, rows, columns, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, stored_path, rows, columns, uploaded_at))
        conn.commit()
        return cursor.lastrowid

def get_dataset(dataset_id: int):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def latest_dataset():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM datasets ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
