from jobomation.db.connection import connect
from jobomation.models import Job

def save_job(job: Job) -> None:
    with connect() as connection:
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
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, source_job_id)
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                url = excluded.url,
                first_published = excluded.first_published,
                updated_at = excluded.updated_at,
                description = excluded.description
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
            ),
        )


def save_jobs(jobs: list[Job]) -> None:
    with connect() as connection:
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
                description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source, source_job_id)
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                url = excluded.url,
                first_published = excluded.first_published,
                updated_at = excluded.updated_at,
                description = excluded.description
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
                )
                for job in jobs
            ],
        )