from pathlib import Path
from sqlite3 import Connection, Row, connect as connect_sqlite

DATABASE_PATH = Path("data/jobomation.db")
"""Path to SQLite database for jobs storage."""

def connect(database: Path = DATABASE_PATH) -> Connection:
    """
    Open SQLite database connection for job storage.

    Args:
        database (Path, optional): Path to SQLite database file. Defaults to `DATABASE_PATH`.

    Returns:
        Connection: SQLite connection with row dictionaries and foreign key enforcement enabled.
    """
    connection = connect_sqlite(database)
    connection.row_factory = Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection