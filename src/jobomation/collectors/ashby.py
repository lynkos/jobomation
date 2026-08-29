from httpx import Response, get as get_request
from jobomation.models import Collector
from jobomation.models import Compensation, Job

class AshbyCollector(Collector):
    """
    Collect job postings from Ashby board and normalize them into jobomation Job model.

    Attributes:
        source (str): Job source identifier.
        api_url (str): Base URL for Ashby job board API.
    """
    source: str = "ashby"
    api_url: str = "https://api.ashbyhq.com/posting-api/job-board"

    def __init__(self, board: str) -> None:
        """
        Initialize Ashby collector for given job board.

        Args:
            board (str): Ashby board identifier used to query jobs.
        """
        self.board: str = board

    @staticmethod
    def _raw_to_compensation(raw: dict) -> Compensation:
        """
        Convert Ashby compensation payload to normalized jobomation Compensation object.
        
        Args:
            raw (dict): Raw compensation data from Ashby.

        Returns:
            Compensation: Compensation object populated from raw compensation data.
        """
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
        """
        Convert Ashby job payload to normalized jobomation Job object.

        Args:
            raw (dict): Raw job data from Ashby.

        Returns:
            Job: Job object populated from raw job data, including parsed compensation information.
        """
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

    def _send_request(self) -> Response:
        """
        Send `GET` request to API for configured Ashby job board.

        Returns:
            Response: Raw HTTP response from Ashby.
        """
        return get_request(
            url = f"{self.api_url}/{self.board}",
            params = { "includeCompensation": "true" },
            timeout = self.timeout
        )

    def fetch_jobs(self) -> list[Job]:
        """
        Fetch and normalize all jobs for configured Ashby board.

        Returns:
            list[Job]: List of Job objects converted from raw job payloads returned by Ashby API.
        """
        raw_jobs = self.get_response()["jobs"]
        return [ self._raw_to_job(raw) for raw in raw_jobs ]