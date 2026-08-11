import httpx
import html
from bs4 import BeautifulSoup
from jobomation.models import Job

JOB_COLLECTOR_NAME = "greenhouse"
JOB_COLLECTOR_URL = "https://boards-api.greenhouse.io/v1/boards"

def clean_description(content: str) -> str:
    decoded = html.unescape(content)
    soup = BeautifulSoup(decoded, "html.parser")
    return soup.get_text(separator="\n", strip=True)

# Fetch job by ID
def fetch_job(board: str, job_id: int) -> Job:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs/{job_id}"

    response = httpx.get(url)
    response.raise_for_status()
    raw_job = response.json()

    return Job(
            source=JOB_COLLECTOR_NAME,
            source_job_id=str(raw_job["id"]),
            title=raw_job["title"],
            company=raw_job["company_name"],
            location=raw_job["location"]["name"],
            url=raw_job["absolute_url"],
            first_published=raw_job["first_published"],
            updated_at=raw_job["updated_at"],
            description=clean_description(raw_job["content"]),
        )

# All currently published jobs
def fetch_jobs(board: str) -> list[Job]:
    url = f"{JOB_COLLECTOR_URL}/{board}/jobs"

    response = httpx.get(
        url,
        params={"content": "true"},
    )
    response.raise_for_status()

    raw_jobs = response.json()["jobs"]

    return [
        Job(
            source=JOB_COLLECTOR_NAME,
            source_job_id=str(raw["id"]),
            title=raw["title"],
            company=raw["company_name"],
            location=raw["location"]["name"],
            url=raw["absolute_url"],
            first_published=raw["first_published"],
            updated_at=raw["updated_at"],
            description=clean_description(raw["content"]),
        )
        for raw in raw_jobs
    ]