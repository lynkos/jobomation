from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar
from httpx import HTTPError, Response
from jobomation.exceptions import CollectorRequestError, CollectorResponseError

@dataclass
class Job:
    source: str
    source_job_id: str
    title: str
    company: str
    location: str
    url: str
    first_published: str
    updated_at: str | None
    description: str
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    active: bool = True
    filtered: bool = False
    filter_reason: str | None = None
    compensation: Compensation | None = None

@dataclass
class Target:
    name: str
    source: str
    args: dict[str, Any] = field(default_factory = dict)

@dataclass
class Compensation:
    min_amount: float | None = None
    max_amount: float | None = None
    currency: str | None = None
    interval: str | None = None
    description: str | None = None

class Collector(ABC):
    source: ClassVar[str]
    api_url: ClassVar[str]
    timeout: ClassVar[int] = 10

    @abstractmethod
    def _send_request(self, *args, **kwargs) -> Response:
        """Send a source-specific HTTP request."""
        raise NotImplementedError

    def get_response(self, *args, **kwargs) -> Any:
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
        """Fetch and normalize all jobs for this collector."""
        raise NotImplementedError

    @abstractmethod
    def _raw_to_job(self, raw: dict) -> Job:
        """Convert one source-specific job payload into a Job."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _raw_to_compensation(raw: dict) -> Compensation | None:
        """Convert source-specific compensation data into Compensation."""
        raise NotImplementedError