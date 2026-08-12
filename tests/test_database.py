from datetime import datetime, timezone
from jobomation.db import repository
from jobomation.db.connection import connect
from jobomation.models import Job

def test_schema_created(temp_database):
    with connect(temp_database) as connection:
        columns = connection.execute(
            "PRAGMA table_info(jobs)"
        ).fetchall()

    names = {column["name"] for column in columns}

    assert {
        "id",
        "source",
        "source_job_id",
        "title",
        "company",
        "location",
        "url",
        "first_published",
        "updated_at",
        "description",
        "first_seen_at",
        "last_seen_at",
        "active",
        "filtered",
        "filter_reason",
    } <= names

def test_foreign_keys_enabled(tmp_path):
    database = tmp_path / "test.db"

    with connect(database) as connection:
        enabled = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

    assert enabled == 1

def test_save_and_get_job(temp_database, sample_job):
    repository.save_job(sample_job)

    result = repository.get_job(
        source="greenhouse",
        source_job_id="12345",
    )

    assert result is not None
    assert result.title == "Software Engineer"
    assert result.company == "Example Corp"
    assert result.active is True
    assert result.filtered is False

def test_save_job_does_not_duplicate(temp_database, sample_job):
    repository.save_job(sample_job)
    repository.save_job(sample_job)

    assert repository.count_jobs() == 1

def test_upsert_updates_existing_job(temp_database, sample_job):
    repository.save_job(sample_job)

    sample_job.title = "Software Engineer, Infrastructure"
    sample_job.description = "Updated description"

    repository.save_job(sample_job)

    result = repository.get_job(
        source="greenhouse",
        source_job_id="12345",
    )

    assert repository.count_jobs() == 1
    assert result is not None
    assert result.title == "Software Engineer, Infrastructure"
    assert result.description == "Updated description"

def test_upsert_preserves_first_seen(temp_database, sample_job, monkeypatch):
    class FirstDatetime:
        @classmethod
        def now(cls, tz):
            return datetime(
                2026,
                8,
                11,
                12,
                0,
                tzinfo=timezone.utc,
            )

    monkeypatch.setattr(
        repository,
        "datetime",
        FirstDatetime,
    )

    repository.save_job(sample_job)

    original = repository.get_job(
        source="greenhouse",
        source_job_id="12345",
    )

    class SecondDatetime:
        @classmethod
        def now(cls, tz):
            return datetime(
                2026,
                8,
                12,
                12,
                0,
                tzinfo=timezone.utc,
            )

    monkeypatch.setattr(
        repository,
        "datetime",
        SecondDatetime,
    )

    repository.save_job(sample_job)

    updated = repository.get_job(
        source="greenhouse",
        source_job_id="12345",
    )

    assert original is not None
    assert updated is not None

    assert updated.first_seen_at == original.first_seen_at
    assert updated.last_seen_at != original.last_seen_at

def test_save_jobs(temp_database):
    jobs = [
        Job(
            source="greenhouse",
            source_job_id=str(i),
            title=f"Software Engineer {i}",
            company="Example",
            location="Boston, MA",
            url=f"https://example.com/{i}",
            first_published="2026-08-01T00:00:00+00:00",
            updated_at=None,
            description="Description",
        )
        for i in range(5)
    ]

    repository.save_jobs(jobs)

    assert repository.count_jobs() == 5

def test_get_jobs_returns_all(temp_database, sample_job):
    repository.save_job(sample_job)

    second = Job(
        source="ashby",
        source_job_id="xyz",
        title="Platform Engineer",
        company="Other Corp",
        location="Seattle, WA",
        url="https://example.com/xyz",
        first_published="2026-08-01T00:00:00+00:00",
        updated_at=None,
        description="Description",
    )

    repository.save_job(second)

    jobs = repository.get_jobs()

    assert len(jobs) == 2

def test_get_jobs_filters_visible_jobs(temp_database, sample_job):
    repository.save_job(sample_job)

    filtered = Job(
        source="greenhouse",
        source_job_id="999",
        title="Senior Software Engineer",
        company="Example",
        location="Boston, MA",
        url="https://example.com/999",
        first_published="2026-08-01T00:00:00+00:00",
        updated_at=None,
        description="Description",
        filtered=True,
        filter_reason="title:senior",
    )

    repository.save_job(filtered)

    visible = repository.get_jobs(filtered=False)

    assert len(visible) == 1
    assert visible[0].source_job_id == "12345"

def test_get_jobs_filters_rejected_jobs(temp_database, filtered_job):
    repository.save_job(filtered_job)

    jobs = repository.get_jobs(filtered=True)

    assert len(jobs) == 1
    assert jobs[0].filtered is True
    assert jobs[0].filter_reason == "title:senior"

def test_get_job_unknown_id_returns_none(temp_database):
    assert repository.get_job(
        source="greenhouse",
        source_job_id="does-not-exist",
    ) is None

def test_unique_constraint_is_source_scoped(temp_database):
    greenhouse = Job(
        source="greenhouse",
        source_job_id="123",
        title="One",
        company="Company A",
        location="Boston",
        url="https://example.com/a",
        first_published="2026-01-01",
        updated_at=None,
        description="A",
    )

    ashby = Job(
        source="ashby",
        source_job_id="123",
        title="Two",
        company="Company B",
        location="Seattle",
        url="https://example.com/b",
        first_published="2026-01-01",
        updated_at=None,
        description="B",
    )

    repository.save_job(greenhouse)
    repository.save_job(ashby)

    assert repository.count_jobs() == 2