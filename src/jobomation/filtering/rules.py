from re import search, IGNORECASE
from jobomation.models import Job

def apply_title_filter(job: Job, title_filters: dict[str, list[str]]) -> Job:
    title = job.title.casefold()

    for reason, patterns in title_filters.items():
        for pattern in patterns:
            if search(pattern, title, flags=IGNORECASE):
                job.filtered = True
                job.filter_reason = f"title:{reason}"
                return job

    return job

def apply_filters(job: Job, filters: dict) -> Job:
    job.filtered = False
    job.filter_reason = None

    title_filters = (
        filters
        .get("title", {})
        .get("exclude", {})
    )

    apply_title_filter(job, title_filters)

    return job

def apply_filters_to_jobs(jobs: list[Job], filters: dict) -> list[Job]:
    return [ apply_filters(job, filters) for job in jobs ]