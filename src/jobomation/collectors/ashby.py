import httpx
from jobomation.models import Job

JOB_COLLECTOR_NAME = "ashby"
JOB_COLLECTOR_URL = "https://api.ashbyhq.com/posting-api/job-board"

def _raw_to_job(board: str, raw: dict) -> Job:
    return Job(
        source=JOB_COLLECTOR_NAME,
        source_job_id=str(raw["id"]),
        title=raw["title"],
        company=board,
        location=raw["location"],
        url=raw["jobUrl"],
        first_published=raw["publishedAt"],
        updated_at=raw["publishedAt"],
        description=raw["descriptionPlain"],
    )

def fetch_jobs(board: str) -> list[Job]:
    url = f"{JOB_COLLECTOR_URL}/{board}"

    response = httpx.get(
        url,
        params={"includeCompensation": "true"},
    )
    response.raise_for_status()

    raw_jobs = response.json()["jobs"]

    return [_raw_to_job(board, raw) for raw in raw_jobs]