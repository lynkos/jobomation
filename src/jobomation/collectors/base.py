from abc import ABC, abstractmethod
from typing import ClassVar
from jobomation.models import Compensation, Job

class Collector(ABC):
    source: ClassVar[str]
    api_url: ClassVar[str]

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