from jobomation.db.connection import connect

def initialize_database() -> None:
    with connect() as connection:
        connection.execute("""
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
                UNIQUE(source, source_job_id)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_company
            ON jobs(company)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_first_published
            ON jobs(first_published)
        """)