from jobomation.db.connection import connect
from jobomation.models import Job
from datetime import datetime, timezone
import sqlite3

TRUE = 1
FALSE = 0

def save_job(job: Job) -> None:
    with connect() as connection:
        now = datetime.now(timezone.utc).isoformat()
        
        connection.execute(
            """
            INSERT INTO jobs (
                source,
                source_job_id,
                title,
                company,
                location,
                url,
                first_published,
                updated_at,
                description,
                first_seen_at,
                last_seen_at,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, source_job_id)
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                url = excluded.url,
                first_published = excluded.first_published,
                updated_at = excluded.updated_at,
                description = excluded.description,
                last_seen_at = excluded.last_seen_at,
                active = TRUE
            """,
            (
                job.source,
                job.source_job_id,
                job.title,
                job.company,
                job.location,
                job.url,
                job.first_published,
                job.updated_at,
                job.description,
                now,
                now,
                TRUE
            ),
        )


def save_jobs(jobs: list[Job]) -> None:
    with connect() as connection:
        now = datetime.now(timezone.utc).isoformat()
        
        connection.executemany(
            """
            INSERT INTO jobs (
                source,
                source_job_id,
                title,
                company,
                location,
                url,
                first_published,
                updated_at,
                description,
                first_seen_at,
                last_seen_at,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, source_job_id)
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                url = excluded.url,
                first_published = excluded.first_published,
                updated_at = excluded.updated_at,
                description = excluded.description,
                last_seen_at = excluded.last_seen_at,
                active = TRUE
            """,
            [
                (
                    job.source,
                    job.source_job_id,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.first_published,
                    job.updated_at,
                    job.description,
                    now,
                    now,
                    TRUE
                )
                for job in jobs
            ],
        )

def _row_to_job(row: sqlite3.Row) -> Job:
    return Job(
        source=row["source"],
        source_job_id=row["source_job_id"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        url=row["url"],
        first_published=row["first_published"],
        updated_at=row["updated_at"],
        description=row["description"],
        first_seen_at=row["first_seen_at"],
        last_seen_at=row["last_seen_at"],
        active=bool(row["active"]),
    )

def get_job(source: str, source_job_id: str) -> Job | None:
    with connect() as connection:
        row = connection.execute(
            """
            SELECT
                source,
                source_job_id,
                title,
                company,
                location,
                url,
                first_published,
                updated_at,
                description,
                first_seen_at,
                last_seen_at,
                active
            FROM jobs
            WHERE source = ?
            AND source_job_id = ?
            """,
            (source, source_job_id),
        ).fetchone()

    return _row_to_job(row) if row is not None else None

def get_jobs() -> list[Job]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT
                source,
                source_job_id,
                title,
                company,
                location,
                url,
                first_published,
                updated_at,
                description,
                first_seen_at,
                last_seen_at,
                active
            FROM jobs
            ORDER BY first_seen_at DESC
            """
        ).fetchall()

    return [_row_to_job(row) for row in rows]

def count_jobs() -> int:
    with connect() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]