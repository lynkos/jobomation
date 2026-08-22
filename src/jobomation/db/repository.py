from datetime import datetime, timezone
from jobomation.db.connection import connect
from jobomation.db.mapping import job_to_record, row_to_job
from jobomation.models import Job

UPSERT_IMMUTABLE_COLUMNS = {
    "source",
    "source_job_id",
    "first_seen_at",
    "active"
}

def _build_upsert_query(columns: tuple[str, ...]) -> str:
    column_list = ", ".join(columns)
    placeholders = ", ".join(f":{column}" for column in columns)

    update_columns = (column for column in columns if column not in UPSERT_IMMUTABLE_COLUMNS)

    updates = ",\n".join(
        f"{column} = excluded.{column}"
        for column in update_columns
    )

    return f"""
        INSERT INTO jobs ({column_list})
        VALUES ({placeholders})
        ON CONFLICT(source, source_job_id)
        DO UPDATE SET
            {updates},
            active = TRUE
    """

def save_job(job: Job) -> None:
    seen_at = datetime.now(timezone.utc)
    record = job_to_record(job, seen_at = seen_at)
    query = _build_upsert_query(tuple(record))

    with connect() as connection:
        connection.execute(query, record)

def save_jobs(jobs: list[Job]) -> None:
    if not jobs: return

    seen_at = datetime.now(timezone.utc)
    records = [ job_to_record(job, seen_at = seen_at) for job in jobs ]

    query = _build_upsert_query(tuple(records[0]))

    with connect() as connection:
        connection.executemany(query, records)

def get_job(*, source: str, source_job_id: str, filtered: bool | None = None) -> Job | None:
    query = """
        SELECT *
        FROM jobs
        WHERE source = :source
        AND source_job_id = :source_job_id
    """

    params: dict[str, object] = {
        "source": source,
        "source_job_id": source_job_id,
    }

    if filtered is not None:
        query += " AND filtered = :filtered"
        params["filtered"] = int(filtered)

    with connect() as connection:
        row = connection.execute(query, params).fetchone()

    return row_to_job(row) if row is not None else None

def get_jobs(*, filtered: bool | None = None) -> list[Job]:
    query = """
        SELECT *
        FROM jobs
    """

    params: dict[str, object] = { }

    if filtered is not None:
        query += " WHERE filtered = :filtered"
        params["filtered"] = int(filtered)

    query += " ORDER BY first_seen_at DESC"

    with connect() as connection:
        rows = connection.execute(query, params).fetchall()

    return [ row_to_job(row) for row in rows ]

def count_jobs() -> int:
    with connect() as connection:
        row = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()

    return row[0]

def set_job_active(*, source: str, source_job_id: str, active: bool) -> None:
    with connect() as connection:
        connection.execute(
            """
            UPDATE jobs
            SET active = :active
            WHERE source = :source
            AND source_job_id = :source_job_id
            """,
            {
                "active": int(active),
                "source": source,
                "source_job_id": source_job_id,
            },
        )