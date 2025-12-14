# Purpose: Connect to and close the database
#same code from week8

import sqlite3
from pathlib import Path


DB_PATH = Path("DATA") / "platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))