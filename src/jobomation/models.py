from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar
from httpx import HTTPError, Response
from jobomation.exceptions import CollectorRequestError, CollectorResponseError

@dataclass
class Job:
    """
    Normalized representation of a single job listing.
    """

    # Canonical source
    source: str

    # External job identifier
    source_job_id: str

    # Metadata
    title: str
    company: str
    location: str
    url: str

    # Rendered description
    description: str

    # Normalized timestamps
    first_published: str
    updated_at: str | None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    # Active status
    active: bool = True

    # Filtered state
    filtered: bool = False
    filter_reason: str | None = None

    # Compensation details
    compensation: Compensation | None = None

    # Content hash used for change detection
    content_hash: str | None = None

@dataclass
class Target:
    """
    Configuration for job source to collect from.
    """
    
    # Human-readable name
    name: str

    # Collector source key
    source: str

    # Keyword arguments used to initialize collector
    args: dict[str, Any] = field(default_factory = dict)

@dataclass
class Compensation:
    """
    Normalized salary and/or pay-range information for a job listing.
    """
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None
    interval: str | None = None
    description: str | None = None

class Collector(ABC):
    """
    Base class for collectors. Collect job postings from job boards and normalize them into jobomation Job model.

    Attributes:
        source (str): Job source identifier.
        api_url (str): Base URL for job board / collector API.
        timeout (int, optional): Timeout config to use when sending request. Defaults to 10.
    """
    source: ClassVar[str]
    api_url: ClassVar[str]
    timeout: ClassVar[int] = 10

    @abstractmethod
    def _send_request(self, *args, **kwargs) -> Response:
        """
        Issue source-specific HTTP request used to fetch raw job data.

        Raises:
            NotImplementedError: Raised when collector doesn't override method.

        Returns:
            Response: HTTP response returned by collector's client.
        """
        raise NotImplementedError

    def get_response(self, *args, **kwargs) -> Any:
        """
        Execute collector request via `_send_request()` and return parsed JSON payload.

        Raises:
            CollectorRequestError: HTTP failures.
            CollectorResponseError: Invalid JSON payload.

        Returns:
            Any: Decoded JSON response.
        """
        try:
            response = self._send_request(*args, **kwargs)
            response.raise_for_status()

        except HTTPError as error:
            raise CollectorRequestError(f"Failed to request jobs from {self.source}") from error

        try:
            return response.json()

        except ValueError as error:
            raise CollectorResponseError(f"Invalid response from {self.source}") from error

    @abstractmethod
    def fetch_jobs(self) -> list[Job]:
        """
        Fetch and normalize all jobs.

        Raises:
            NotImplementedError: Collector doesn't override this method.

        Returns:
            list[Job]: List of normalized Job objects.
        """
        raise NotImplementedError

    @abstractmethod
    def _raw_to_job(self, raw: dict) -> Job:
        """
        Convert source-specific job payload into normalized Job object.

        Args:
            raw (dict): Job record returned by source API.

        Raises:
            NotImplementedError: Collector doesn't override this method.

        Returns:
            Job: Normalized Job object.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _raw_to_compensation(raw: dict) -> Compensation | None:
        """
        Convert source-specific compensation data into Compensation object.

        Args:
            raw (dict): Compensation data returned by source API.

        Raises:
            NotImplementedError: Collector doesn't override this method.

        Returns:
            Compensation | None: Normalized Compensation object
            or None when no compensation information is available.
        """
        raise NotImplementedError