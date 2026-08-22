from sqlite3 import Row
from datetime import datetime
from jobomation.models import Compensation, Job

def job_to_record(job: Job, *, seen_at: datetime) -> dict[str, object]:
    compensation = job.compensation

    return {
        "source": job.source,
        "source_job_id": job.source_job_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "first_published": job.first_published,
        "updated_at": job.updated_at,
        "description": job.description,

        "compensation_min_amount": compensation.min_amount if compensation else None,
        "compensation_max_amount": compensation.max_amount if compensation else None,
        "compensation_currency": compensation.currency if compensation else None,
        "compensation_interval": compensation.interval if compensation else None,
        "compensation_description": compensation.description if compensation else None,

        "first_seen_at": seen_at.isoformat(),
        "last_seen_at": seen_at.isoformat(),

        "active": int(job.active),
        "filtered": int(job.filtered),
        "filter_reason": job.filter_reason,
    }

def row_to_compensation(row: Row) -> Compensation | None:
    if all(
        row[column] is None
        for column in (
            "compensation_min_amount",
            "compensation_max_amount",
            "compensation_currency",
            "compensation_interval",
            "compensation_description",
        )
    ):
        return None

    return Compensation(
        min_amount = row["compensation_min_amount"],
        max_amount = row["compensation_max_amount"],
        currency = row["compensation_currency"],
        interval = row["compensation_interval"],
        description = row["compensation_description"],
    )

def row_to_job(row: Row) -> Job:
    return Job(
        source = row["source"],
        source_job_id = row["source_job_id"],
        title = row["title"],
        company = row["company"],
        location = row["location"],
        url = row["url"],
        first_published = row["first_published"],
        updated_at = row["updated_at"],
        description = row["description"],
        first_seen_at = _parse_datetime(row["first_seen_at"]),
        last_seen_at = _parse_datetime(row["last_seen_at"]),
        active = bool(row["active"]),
        filtered = bool(row["filtered"]),
        filter_reason = row["filter_reason"],
        compensation = row_to_compensation(row)
    )

def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value is not None else None