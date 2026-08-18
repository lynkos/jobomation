from unittest.mock import Mock

from jobomation.collectors import (
    COLLECTORS,
    AshbyCollector,
    GreenhouseCollector,
    IndeedCollector,
)
from jobomation.collectors import ashby, greenhouse, indeed
from jobomation.collectors.base import Collector
from jobomation.collectors.utils import clean_description


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
        "pay_input_ranges": [],
    }


def ashby_raw_job(job_id="abc-123"):
    return {
        "id": job_id,
        "title": "Software Engineer",
        "location": "New York, NY",
        "jobUrl": f"https://jobs.ashbyhq.com/example/{job_id}",
        "publishedAt": "2026-08-01T12:00:00+00:00",
        "descriptionPlain": "Build software and systems.",
        "compensation": {
            "summaryComponents": [
                {
                    "compensationType": "Salary",
                    "minValue": 100_000,
                    "maxValue": 150_000,
                    "currencyCode": "USD",
                    "interval": "YEAR",
                }
            ],
            "compensationTierSummary": "$100K – $150K",
        },
    }


def indeed_raw_job(job_id="abc123"):
    return {
        "key": job_id,
        "title": "Software Engineer",
        "datePublished": 1785600000000,
        "dateOnIndeed": 1000,
        "description": {
            "html": "<p>Build software and systems.</p>",
        },
        "location": {
            "countryName": "United States",
            "countryCode": "US",
            "admin1Code": "MA",
            "city": "Boston",
            "postalCode": "02108",
            "streetAddress": None,
            "formatted": {
                "short": "Boston, MA",
                "long": "Boston, MA, United States",
            },
        },
        "compensation": None,
        "attributes": [],
        "employer": {
            "relativeCompanyPageUrl": "/cmp/Example",
            "name": "Example Corp",
        },
        "recruit": None,
    }


def test_clean_description():
    content = (
        "&lt;h2&gt;About&lt;/h2&gt;"
        "&lt;p&gt;Hello &amp; goodbye&lt;/p&gt;"
    )

    result = clean_description(content)

    assert "About" in result
    assert "Hello & goodbye" in result
    assert "<h2>" not in result


def test_greenhouse_raw_to_job():
    collector = GreenhouseCollector("example")
    job = collector._raw_to_job(greenhouse_raw_job())

    assert job.source == "greenhouse"
    assert job.source_job_id == "123"
    assert job.title == "Software Engineer"
    assert job.company == "Example Corp"
    assert job.location == "Boston, MA"
    assert job.description == "About\nBuild software & systems."


def test_greenhouse_fetch_job(monkeypatch):
    response = Mock()
    response.json.return_value = greenhouse_raw_job(42)

    mocked_get = Mock(return_value=response)
    monkeypatch.setattr(greenhouse, "get_request", mocked_get)

    collector = GreenhouseCollector("example")
    job = collector.fetch_job(42)

    mocked_get.assert_called_once_with(
        f"{collector.api_url}/example/jobs/42",
        params={"pay_transparency": "true"},
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
    monkeypatch.setattr(greenhouse, "get_request", mocked_get)

    collector = GreenhouseCollector("example")
    jobs = collector.fetch_jobs()

    mocked_get.assert_called_once()

    _, kwargs = mocked_get.call_args

    assert kwargs["params"]["content"] == "true"
    assert kwargs["params"]["pay_transparency"] == "true"

    response.raise_for_status.assert_called_once()

    assert len(jobs) == 2
    assert jobs[0].source_job_id == "1"
    assert jobs[1].source_job_id == "2"

def test_ashby_raw_to_job():
    collector = AshbyCollector("example")
    job = collector._raw_to_job(ashby_raw_job())

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
    monkeypatch.setattr(ashby, "get_request", mocked_get)

    collector = AshbyCollector("ramp")
    jobs = collector.fetch_jobs()

    mocked_get.assert_called_once()

    _, kwargs = mocked_get.call_args

    assert kwargs["params"]["includeCompensation"] == "true"

    response.raise_for_status.assert_called_once()

    assert len(jobs) == 2
    assert all(job.source == "ashby" for job in jobs)

def test_indeed_raw_to_job():
    collector = IndeedCollector(
        search_term="software engineer",
        location="Boston, MA",
    )

    job = collector._raw_to_job(indeed_raw_job())

    assert job.source == "indeed"
    assert job.source_job_id == "abc123"
    assert job.title == "Software Engineer"
    assert job.company == "Example Corp"
    assert job.location == "Boston, MA, United States"
    assert job.url.endswith("/viewjob?jk=abc123")
    assert job.updated_at is None
    assert "Build software and systems." in job.description


def test_indeed_build_query():
    collector = IndeedCollector(
            search_term="software engineer",
            location="Boston, MA",
            radius=200
        )
    query = collector._build_query(
        search_term="software engineer",
        location="Boston, MA",
        cursor="cursor-123"
    )

    assert 'what: "software engineer"' in query
    assert 'where: "Boston, MA"' in query
    assert 'cursor: "cursor-123"' in query
    assert "radius: 200" in query

def test_indeed_fetch_page(monkeypatch):
    response = Mock()

    response.json.return_value = {
        "data": {
            "jobSearch": {
                "results": [
                    {
                        "job": indeed_raw_job("one"),
                    },
                    {
                        "job": indeed_raw_job("two"),
                    },
                ],
                "pageInfo": {
                    "nextCursor": "next-page",
                },
            }
        }
    }

    mocked_post = Mock(return_value=response)

    monkeypatch.setattr(
        indeed,
        "post_request",
        mocked_post,
    )
    monkeypatch.setenv("INDEED_API_KEY", "test-key")

    collector = IndeedCollector(
        search_term="software engineer",
        location="Boston, MA",
        radius=200,
    )

    results, cursor = collector._fetch_page()

    response.raise_for_status.assert_called_once()

    assert len(results) == 2
    assert cursor == "next-page"

    args, kwargs = mocked_post.call_args

    assert args[0] == collector.api_url
    assert kwargs["timeout"] == collector.timeout

    query = kwargs["json"]["query"]

    assert 'what: "software engineer"' in query
    assert 'where: "Boston, MA"' in query
    assert "radius: 200" in query


def test_indeed_fetch_jobs(monkeypatch):
    first_page = [
        {"job": indeed_raw_job("one")},
        {"job": indeed_raw_job("two")},
    ]

    second_page = [
        {"job": indeed_raw_job("three")},
    ]

    mocked_fetch_page = Mock(
        side_effect=[
            (first_page, "cursor-2"),
            (second_page, None),
        ]
    )

    collector = IndeedCollector(
        search_term="software engineer",
        location="Boston, MA",
        radius=200,
        results_wanted=3,
    )

    monkeypatch.setattr(
        collector,
        "_fetch_page",
        mocked_fetch_page,
    )

    jobs = collector.fetch_jobs()

    assert [job.source_job_id for job in jobs] == [
        "one",
        "two",
        "three",
    ]

    assert mocked_fetch_page.call_count == 2

    mocked_fetch_page.assert_any_call(None)
    mocked_fetch_page.assert_any_call("cursor-2")


def test_indeed_fetch_jobs_deduplicates(monkeypatch):
    mocked_fetch_page = Mock(
        return_value=(
            [
                {"job": indeed_raw_job("one")},
                {"job": indeed_raw_job("one")},
            ],
            None,
        )
    )

    collector = IndeedCollector(
        search_term="software engineer",
        location="Boston, MA",
        radius=200,
        results_wanted=100,
    )

    monkeypatch.setattr(
        collector,
        "_fetch_page",
        mocked_fetch_page,
    )

    jobs = collector.fetch_jobs()

    assert len(jobs) == 1
    assert jobs[0].source_job_id == "one"

    mocked_fetch_page.assert_called_once_with(None)


def test_collectors_inherit_from_base():
    assert issubclass(GreenhouseCollector, Collector)
    assert issubclass(AshbyCollector, Collector)
    assert issubclass(IndeedCollector, Collector)


def test_collector_registry():
    assert COLLECTORS["greenhouse"] is GreenhouseCollector
    assert COLLECTORS["ashby"] is AshbyCollector
    assert COLLECTORS["indeed"] is IndeedCollector