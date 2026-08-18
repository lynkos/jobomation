from httpx import get as get_request
from jobomation.collectors.base import Collector
from jobomation.models import Compensation, Job
from jobomation.collectors.utils import clean_description

class GreenhouseCollector(Collector):
    source = "greenhouse"
    api_url = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, board: str) -> None:
        self.board = board

    @staticmethod
    def _raw_to_compensation(raw: dict) -> Compensation:
        pay = raw[0]
        
        return Compensation(
            min_amount = pay["min_cents"] / 100,
            max_amount = pay["max_cents"] / 100,
            currency = pay["currency_type"],
            interval = None,
            description = f"{pay["title"]} -- {pay["blurb"]}"
        )

    def _raw_to_job(self, raw: dict) -> Job:
        return Job(
            source = self.source,
            source_job_id = str(raw["id"]),
            title = raw["title"],
            company = raw["company_name"],
            location = raw["location"]["name"],
            url = raw["absolute_url"],
            first_published = raw["first_published"],
            updated_at = raw["updated_at"],
            description = clean_description(raw["content"]),
            compensation = self._raw_to_compensation(raw["pay_input_ranges"]) if raw["pay_input_ranges"] else None
        )

    def fetch_jobs(self) -> list[Job]:
        response = get_request(
            url = f"{self.api_url}/{self.board}/jobs",
            params = { "content": "true", "pay_transparency": "true" }
        )
        response.raise_for_status()

        raw_jobs = response.json()["jobs"]

        return [self._raw_to_job(raw) for raw in raw_jobs]

    def fetch_job(self, job_id: int | str) -> Job:
        url = f"{self.api_url}/{self.board}/jobs/{job_id}"

        response = get_request(url, params = { "pay_transparency": "true" })
        response.raise_for_status()
        raw_job = response.json()

        return self._raw_to_job(raw_job)