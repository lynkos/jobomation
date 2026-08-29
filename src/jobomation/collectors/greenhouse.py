from httpx import Response, get as get_request
from jobomation.models import Collector
from jobomation.models import Compensation, Job
from jobomation.collectors.utils import clean_description

class GreenhouseCollector(Collector):
    """
    Collect job postings from Greenhouse board and normalize them into jobomation Job model.

    Attributes:
        source (str): Job source identifier.
        api_url (str): Base URL for Greenhouse job board API.
    """
    source = "greenhouse"
    api_url = "https://boards-api.greenhouse.io/v1/boards"

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
        Convert Greenhouse compensation payload to normalized jobomation Compensation object.
        
        Args:
            raw (dict): Raw compensation data from Greenhouse.

        Returns:
            Compensation: Compensation object populated from raw compensation data.
        """
        pay = raw[0]
        
        return Compensation(
            min_amount = pay["min_cents"] / 100,
            max_amount = pay["max_cents"] / 100,
            currency = pay["currency_type"],
            interval = None,
            description = f"{pay["title"]} -- {clean_description(pay["blurb"])}"
        )

    def _raw_to_job(self, raw: dict) -> Job:
        """
        Convert Greenhouse job payload to normalized jobomation Job object.

        Args:
            raw (dict): Raw job data from Greenhouse.

        Returns:
            Job: Job object populated from raw job data, including parsed compensation information.
        """
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

    def _send_request(self, job_id: int | str | None = None) -> Response:
        """
        Send `GET` request to API for configured Greenhouse job board or specific job.

        Args:
            job_id (int | str | None, optional): Optional identifier for a particular job. Defaults to None.

        Returns:
            Response: Raw HTTP response from Greenhouse.
        """
        if job_id is not None:
            url = f"{self.api_url}/{self.board}/jobs/{job_id}"
            params = { "pay_transparency": "true" }

        else:
            url = f"{self.api_url}/{self.board}/jobs"
            params = { "content": "true", "pay_transparency": "true" }

        return get_request(url, params = params, timeout = self.timeout)

    def fetch_job(self, job_id: int | str) -> Job:
        """
        Fetch and normalize specified job from configured Greenhouse board.

        Args:
            job_id (int | str): Identifier for a particular job.

        Returns:
            Job: Job object converted from raw job payload returned by Greenhouse API.
        """
        return self._raw_to_job(self.get_response(job_id))

    def fetch_jobs(self) -> list[Job]:
        """
        Fetch and normalize all jobs for configured Greenhouse board.

        Returns:
            list[Job]: List of Job objects converted from raw job payloads returned by Greenhouse API.
        """
        raw_jobs = self.get_response()["jobs"]
        return [ self._raw_to_job(raw) for raw in raw_jobs ]