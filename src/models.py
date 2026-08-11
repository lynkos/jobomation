from dataclasses import dataclass

@dataclass
class Job:
    job_id: int
    title: str
    company: str
    location: str
    url: str
    first_published: str
    updated_at: str
    description: str