from httpx import get as get_request
from jobomation.collectors.base import Collector
from jobomation.models import Compensation, Job

class AshbyCollector(Collector):
    source = "ashby"
    api_url = "https://api.ashbyhq.com/posting-api/job-board"

    def __init__(self, board: str) -> None:
        self.board = board

    @staticmethod
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
            min_amount = min_amount,
            max_amount = max_amount,
            currency = currency,
            interval = interval,
            description = raw["compensationTierSummary"]
        )

    def _raw_to_job(self, raw: dict) -> Job:
        return Job(
            source = self.source,
            source_job_id = raw["id"],
            title = raw["title"],
            company = self.board,
            location = raw["location"],
            url = raw["jobUrl"],
            first_published = raw["publishedAt"],
            updated_at = raw["publishedAt"],
            description = raw["descriptionPlain"],
            compensation = self._raw_to_compensation(raw["compensation"])
        )

    def fetch_jobs(self) -> list[Job]:
        response = get_request(
            url = f"{self.api_url}/{self.board}",
            params = {"includeCompensation": "true"},
        )
        response.raise_for_status()

        raw_jobs = response.json()["jobs"]

        return [self._raw_to_job(raw) for raw in raw_jobs]