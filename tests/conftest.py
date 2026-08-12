import pytest
from jobomation.db import connection, repository, schema
from jobomation.models import Job

@pytest.fixture
def sample_job() -> Job:
    return Job(
        source="greenhouse",
        source_job_id="12345",
        title="Software Engineer",
        company="Example Corp",
        location="Boston, MA",
        url="https://example.com/jobs/12345",
        first_published="2026-08-01T12:00:00+00:00",
        updated_at="2026-08-02T12:00:00+00:00",
        description="Build interesting software.",
    )

@pytest.fixture
def filtered_job(sample_job: Job) -> Job:
    sample_job.filtered = True
    sample_job.filter_reason = "title:senior"
    return sample_job

@pytest.fixture
def temp_database(tmp_path, monkeypatch):
    database_path = tmp_path / "jobomation-test.db"

    def test_connect():
        return connection.connect(database_path)

    monkeypatch.setattr(repository, "connect", test_connect)
    monkeypatch.setattr(schema, "connect", test_connect)

    schema.initialize_database()

    return database_path