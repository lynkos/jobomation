from jobomation.db.connection import connect

CREATE_JOBS_TABLE = """
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        source TEXT NOT NULL,
        source_job_id TEXT NOT NULL,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        url TEXT NOT NULL,
        first_published TEXT,
        updated_at TEXT,
        description TEXT,

        compensation_min_amount REAL,
        compensation_max_amount REAL,
        compensation_currency TEXT,
        compensation_interval TEXT,
        compensation_description TEXT,

        first_seen_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,

        active INTEGER NOT NULL DEFAULT 1
            CHECK (active IN (0, 1)),

        filtered INTEGER NOT NULL DEFAULT 0
            CHECK (filtered IN (0, 1)),

        filter_reason TEXT,

        UNIQUE(source, source_job_id)
    )
"""

CREATE_INDEXES = (
    """
    CREATE INDEX IF NOT EXISTS idx_jobs_company
    ON jobs(company)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_jobs_first_published
    ON jobs(first_published)
    """
)

def initialize_database() -> None:
    with connect() as connection:
        connection.execute(CREATE_JOBS_TABLE)

        for query in CREATE_INDEXES:
            connection.execute(query)