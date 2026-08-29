from re import search, IGNORECASE
from jobomation.models import Job

def apply_title_filter(job: Job, title_filters: dict[str, list[str]]) -> Job:
    """
    Mark job as filtered when its title matches configured exclusion pattern.

    Args:
        job (Job): Job being evaluated.
        title_filters (dict[str, list[str]]): Mapping of exclusion reasons to regex filter patterns.

    Returns:
        Job: Filtered Job object with reason set to "title:<reason>" when match found, else Job is unchanged.
    """
    title = job.title.casefold()

    for reason, patterns in title_filters.items():
        for pattern in patterns:
            if search(pattern, title, flags = IGNORECASE):
                job.filtered = True
                job.filter_reason = f"title:{reason}"
                return job

    return job

def apply_filters(job: Job, filters: dict) -> Job:
    """
    Reset job's filter state and apply configured title exclusion rules.

    Args:
        job (Job): Job to evaluate.
        filters (dict): Filter configuration mapping, including title exclusion patterns.

    Returns:
        Job: Job object after clearing prior filter state and applying title-based filtering rules.
    """
    job.filtered = False
    job.filter_reason = None

    title_filters = (
        filters
        .get("title", { })
        .get("exclude", { })
    )

    apply_title_filter(job, title_filters)

    return job

def apply_filters_to_jobs(jobs: list[Job], filters: dict) -> list[Job]:
    """
    Apply configured filtering rules to all jobs.

    Args:
        jobs (list[Job]): Jobs to evaluate.
        filters (dict): Filters used to reset and apply exclusion rules for each job.

    Returns:
        list[Job]: List of jobs after filtering, in original order.
    """
    return [ apply_filters(job, filters) for job in jobs ]