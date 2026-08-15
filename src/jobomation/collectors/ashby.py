from httpx import get as get_request
from jobomation.models import Compensation, Job

JOB_COLLECTOR_NAME = "ashby"
JOB_COLLECTOR_URL = "https://api.ashbyhq.com/posting-api/job-board"

def _raw_to_compensation(raw: dict) -> Compensation:
    min_amount = max_amount = currency = interval = None
    
    for component in raw["summaryComponents"]:
        if component["compensationType"] == "Salary":
            min_amount = component["minValue"]
            max_amount = component["maxValue"]
            currency = component["currencyCode"]
            interval = component["interval"]
            break
        
    return Compensation(
        min_amount=min_amount,
        max_amount=max_amount,
        currency=currency,
        interval=interval,
        description=raw["compensationTierSummary"]
    )
    
def _raw_to_job(board: str, raw: dict) -> Job:    
    return Job(
        source=JOB_COLLECTOR_NAME,
        source_job_id=raw["id"],
        title=raw["title"],
        company=board,
        location=raw["location"],
        url=raw["jobUrl"],
        first_published=raw["publishedAt"],
        updated_at=raw["publishedAt"],
        description=raw["descriptionPlain"],
        compensation=_raw_to_compensation(raw["compensation"])
    )

def fetch_jobs(board: str) -> list[Job]:
    url = f"{JOB_COLLECTOR_URL}/{board}"

    response = get_request(
        url,
        params={"includeCompensation": "true"},
    )
    response.raise_for_status()

    raw_response = response.json()["jobs"]

    return [_raw_to_job(board, raw) for raw in raw_response]