from pathlib import Path
import sqlite3

DATABASE_PATH = Path("data/jobomation.db")

def connect(database: Path = DATABASE_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection