#a code made to connect everythign together and make the database tables similar to how its done in week8 lab file that was given
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "platform.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS security_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        incident_type TEXT,
        severity TEXT,
        status TEXT,
        description TEXT,
        reported_by TEXT,
        created_at TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized:", DB_PATH)

if __name__ == "__main__":
    init_db()