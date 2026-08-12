from jobomation.models import Company, Job

def test_job_defaults():
    job = Job(
        source="greenhouse",
        source_job_id="123",
        title="Software Engineer",
        company="Example",
        location="Seattle, WA",
        url="https://example.com/123",
        first_published="2026-08-01T00:00:00+00:00",
        updated_at=None,
        description="Description",
    )

    assert job.active is True
    assert job.filtered is False
    assert job.filter_reason is None
    assert job.first_seen_at is None
    assert job.last_seen_at is None

def test_company():
    company = Company(
        name="DoorDash",
        source_type="greenhouse",
        board_id="doordashusa",
    )

    assert company.name == "DoorDash"
    assert company.source_type == "greenhouse"
    assert company.board_id == "doordashusa"