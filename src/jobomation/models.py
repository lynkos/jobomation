from dataclasses import dataclass
from datetime import datetime

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