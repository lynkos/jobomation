from jobomation.filtering.rules import apply_filters, apply_filters_to_jobs, apply_title_filter
from jobomation.models import Job

TITLE_FILTERS = {
    "senior": [
        r"\bsenior\b",
        r"\bsr\.?(?=\s|$|[,/-])",
    ],
    "staff": [
        r"\bstaff\b",
    ],
    "principal": [
        r"\bprincipal\b",
    ],
}

def make_job(title: str) -> Job:
    return Job(
        source="greenhouse",
        source_job_id="123",
        title=title,
        company="Example",
        location="Boston, MA",
        url="https://example.com",
        first_published="2026-08-01T00:00:00+00:00",
        updated_at=None,
        description="Description",
    )

def test_title_filter_excludes_senior():
    job = make_job("Senior Software Engineer")

    result = apply_title_filter(job, TITLE_FILTERS)

    assert result.filtered is True
    assert result.filter_reason == "title:senior"

def test_title_filter_is_case_insensitive():
    job = make_job("SENIOR SOFTWARE ENGINEER")

    result = apply_title_filter(job, TITLE_FILTERS)

    assert result.filtered is True
    assert result.filter_reason == "title:senior"

def test_title_filter_matches_sr():
    job = make_job("Sr. Software Engineer")

    result = apply_title_filter(job, TITLE_FILTERS)

    assert result.filtered is True
    assert result.filter_reason == "title:senior"

def test_title_filter_allows_normal_swe():
    job = make_job("Software Engineer")

    result = apply_title_filter(job, TITLE_FILTERS)

    assert result.filtered is False
    assert result.filter_reason is None

def test_filter_does_not_match_substrings():
    job = make_job("Staffing Software Engineer")

    result = apply_title_filter(job, TITLE_FILTERS)

    assert result.filtered is False

def test_apply_filters_resets_previous_filter_state():
    job = make_job("Software Engineer")

    job.filtered = True
    job.filter_reason = "old:filter"

    filters = {
        "title": {
            "exclude": TITLE_FILTERS,
        }
    }

    result = apply_filters(job, filters)

    assert result.filtered is False
    assert result.filter_reason is None

def test_apply_filters_handles_empty_configuration():
    job = make_job("Senior Software Engineer")

    result = apply_filters(job, {})

    assert result.filtered is False
    assert result.filter_reason is None

def test_apply_filters_to_jobs():
    jobs = [
        make_job("Software Engineer"),
        make_job("Senior Software Engineer"),
        make_job("Staff Software Engineer"),
    ]

    filters = {
        "title": {
            "exclude": TITLE_FILTERS,
        }
    }

    results = apply_filters_to_jobs(jobs, filters)

    assert len(results) == 3
    assert results[0].filtered is False
    assert results[1].filtered is True
    assert results[2].filtered is True