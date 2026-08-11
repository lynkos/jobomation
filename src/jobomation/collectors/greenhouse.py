import httpx
import html
from bs4 import BeautifulSoup
from jobomation.models import Job

JOB_COLLECTOR_NAME = "greenhouse"
JOB_COLLECTOR_URL = "https://boards-api.greenhouse.io/v1/boards"

def _clean_description(content: str) -> str:
    decoded = html.unescape(content)
    soup = BeautifulSoup(decoded, "html.parser")
    return soup.get_text(separator="\n", strip=True)

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
        description=_clean_description(raw["content"])
    )

# Fetch job by ID
def fetch_job(board: str, job_id: int | str) -> Job:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs/{job_id}"

    response = httpx.get(url)
    response.raise_for_status()
    raw_job = response.json()

    return _raw_to_job(raw_job)

# All currently published jobs
def fetch_jobs(board: str) -> list[Job]:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs"

    response = httpx.get(
        url,
        params={"content": "true"},
    )
    response.raise_for_status()

    raw_jobs = response.json()["jobs"]

    return [_raw_to_job(raw) for raw in raw_jobs]