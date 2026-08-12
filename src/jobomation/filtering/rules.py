import re
from jobomation.models import Job

EXCLUDED_TITLE_PATTERNS = {
    "senior": r"\bsenior\b",
    "sr": r"\bsr\.?(?=\s|$|[,/-])",
    "staff": r"\bstaff\b",
    "principal": r"\bprincipal\b",
    "manager": r"\bmanager\b",
    "director": r"\bdirector\b",
}

def apply_title_filter(job: Job) -> Job:
    title = job.title.casefold()

    for reason, pattern in EXCLUDED_TITLE_PATTERNS.items():
        if re.search(pattern, title):
            job.filtered = True
            job.filter_reason = f"title:{reason}"
            return job

    return job

def apply_filters(job: Job) -> Job:
    job.filtered = False
    job.filter_reason = None

    apply_title_filter(job)

    return job

def apply_filters_to_jobs(jobs: list[Job]) -> list[Job]:
    return [apply_filters(job) for job in jobs]