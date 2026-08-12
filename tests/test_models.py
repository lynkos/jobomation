from jobomation.models import Target, Job

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

def test_collection_target():
    target = Target(
        name="DoorDash",
        source_type="greenhouse",
        args={
            "board": "doordashusa",
        },
    )

    assert target.name == "DoorDash"
    assert target.source_type == "greenhouse"
    assert target.args == {
        "board": "doordashusa",
    }

def test_collection_target_defaults_to_empty_args():
    target = Target(
        name="Example",
        source_type="test",
    )

    assert target.args == {}