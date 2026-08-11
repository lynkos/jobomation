import httpx
import html
from bs4 import BeautifulSoup
from src.models import Job

def clean_description(content: str) -> str:
    decoded = html.unescape(content)
    soup = BeautifulSoup(decoded, "html.parser")
    return soup.get_text(separator="\n", strip=True)

# Fetch job by ID
def fetch_job(board: str, job_id: int) -> Job:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}"

    response = httpx.get(url)
    response.raise_for_status()

    raw_job = response.json()

    return Job(
            job_id=raw_job["id"],
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
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"

    response = httpx.get(
        url,
        params={"content": "true"},
    )
    response.raise_for_status()

    raw_jobs = response.json()["jobs"]

    return [
        Job(
            job_id=raw["id"],
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

# Get all DoorDash jobs
jobs = fetch_jobs("doordashusa")

print(f"Found {len(jobs)} jobs")
first_job = jobs[0]
print(first_job.job_id)

# Get specific DoorDash job
job = fetch_job("doordashusa", 7263610)

print(job.title)
print(job.location)
