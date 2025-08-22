import sqlite3
from pathlib import Path

DB = "fitness.db"

def get_db_connection():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn