from httpx import get as get_request
from jobomation.models import Compensation, Job
from jobomation.collectors.utils import clean_description

JOB_COLLECTOR_NAME = "greenhouse"
JOB_COLLECTOR_URL = "https://boards-api.greenhouse.io/v1/boards"

def _raw_to_compensation(raw: dict) -> Compensation:
    pay = raw[0]
        
    return Compensation(
        min_amount=pay["min_cents"] / 100,
        max_amount=pay["max_cents"] / 100,
        currency=pay["currency_type"],
        interval=None,
        description=f"{pay["title"]} -- {pay["blurb"]}"
    )

def _raw_to_job(raw: dict) -> Job:
    return Job(
        source=JOB_COLLECTOR_NAME,
        source_job_id=str(raw["id"]),
        title=raw["title"],
        company=raw["company_name"],
        location=raw["location"]["name"],
        url=raw["absolute_url"],
        first_published=raw["first_published"],
        updated_at=raw["updated_at"],
        description=clean_description(raw["content"]),
        compensation=_raw_to_compensation(raw["pay_input_ranges"]) if raw["pay_input_ranges"] else None
    )

# Fetch job by ID
def fetch_job(board: str, job_id: int | str) -> Job:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs/{job_id}"

    response = get_request(
        url,
        params={"pay_transparency": "true"},
    )
    response.raise_for_status()
    raw_job = response.json()

    return _raw_to_job(raw_job)

# All currently published jobs
def fetch_jobs(board: str) -> list[Job]:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs"

    response = get_request(
        url,
        params={"content": "true",
                "pay_transparency": "true"},
    )
    response.raise_for_status()

    raw_jobs = response.json()["jobs"]

    return [_raw_to_job(raw) for raw in raw_jobs]