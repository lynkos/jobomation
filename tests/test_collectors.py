from unittest.mock import Mock
from jobomation.collectors import ashby, greenhouse

def greenhouse_raw_job(job_id=123):
    return {
        "id": job_id,
        "title": "Software Engineer",
        "company_name": "Example Corp",
        "location": {
            "name": "Boston, MA",
        },
        "absolute_url": f"https://example.com/jobs/{job_id}",
        "first_published": "2026-08-01T12:00:00+00:00",
        "updated_at": "2026-08-02T12:00:00+00:00",
        "content": (
            "&lt;h2&gt;About&lt;/h2&gt;"
            "&lt;p&gt;Build software &amp; systems.&lt;/p&gt;"
        ),
    }

def ashby_raw_job(job_id="abc-123"):
    return {
        "id": job_id,
        "title": "Software Engineer",
        "location": "New York, NY",
        "jobUrl": f"https://jobs.ashbyhq.com/example/{job_id}",
        "publishedAt": "2026-08-01T12:00:00+00:00",
        "descriptionPlain": "Build software and systems.",
    }

def test_greenhouse_clean_description():
    content = (
        "&lt;h2&gt;About&lt;/h2&gt;"
        "&lt;p&gt;Hello &amp; goodbye&lt;/p&gt;"
    )

    result = greenhouse._clean_description(content)

    assert "About" in result
    assert "Hello & goodbye" in result
    assert "<h2>" not in result

def test_greenhouse_raw_to_job():
    job = greenhouse._raw_to_job(greenhouse_raw_job())

    assert job.source == "greenhouse"
    assert job.source_job_id == "123"
    assert job.title == "Software Engineer"
    assert job.company == "Example Corp"
    assert job.location == "Boston, MA"
    assert job.description == "About\nBuild software & systems."

def test_greenhouse_fetch_job(monkeypatch):
    response = Mock()
    response.json.return_value = greenhouse_raw_job(42)

    monkeypatch.setattr(
        greenhouse.httpx,
        "get",
        Mock(return_value=response),
    )

    job = greenhouse.fetch_job("example", 42)

    greenhouse.httpx.get.assert_called_once_with(
        f"{greenhouse.JOB_COLLECTOR_URL}/example/jobs/42"
    )

    response.raise_for_status.assert_called_once()

    assert job.source_job_id == "42"

def test_greenhouse_fetch_jobs(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "jobs": [
            greenhouse_raw_job(1),
            greenhouse_raw_job(2),
        ]
    }

    mocked_get = Mock(return_value=response)

    monkeypatch.setattr(
        greenhouse.httpx,
        "get",
        mocked_get,
    )

    jobs = greenhouse.fetch_jobs("example")

    mocked_get.assert_called_once_with(
        f"{greenhouse.JOB_COLLECTOR_URL}/example/jobs",
        params={"content": "true"},
    )

    assert len(jobs) == 2
    assert jobs[0].source_job_id == "1"
    assert jobs[1].source_job_id == "2"

def test_ashby_raw_to_job():
    job = ashby._raw_to_job(
        "example",
        ashby_raw_job(),
    )

    assert job.source == "ashby"
    assert job.source_job_id == "abc-123"
    assert job.company == "example"
    assert job.location == "New York, NY"
    assert job.description == "Build software and systems."

def test_ashby_fetch_jobs(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "jobs": [
            ashby_raw_job("one"),
            ashby_raw_job("two"),
        ]
    }

    mocked_get = Mock(return_value=response)

    monkeypatch.setattr(
        ashby.httpx,
        "get",
        mocked_get,
    )

    jobs = ashby.fetch_jobs("ramp")

    mocked_get.assert_called_once_with(
        f"{ashby.JOB_COLLECTOR_URL}/ramp",
        params={"includeCompensation": "true"},
    )

    response.raise_for_status.assert_called_once()

    assert len(jobs) == 2
    assert all(job.source == "ashby" for job in jobs)

def test_collector_registry():
    from jobomation.collectors import COLLECTORS

    assert COLLECTORS["greenhouse"] is greenhouse.fetch_jobs
    assert COLLECTORS["ashby"] is ashby.fetch_jobs