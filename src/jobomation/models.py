from dataclasses import dataclass

@dataclass
class Job:
    source: str
    source_job_id: str
    title: str
    company: str
    location: str
    url: str
    first_published: str
    updated_at: str
    description: str