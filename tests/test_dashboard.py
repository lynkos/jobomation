from unittest.mock import Mock
from jobomation.models import Job
from jobomation.dashboard import app as dashboard

def make_job() -> Job:
    return Job(
        source="greenhouse",
        source_job_id="123",
        title="Software Engineer",
        company="Example",
        location="Boston, MA",
        url="https://example.com/123",
        first_published="2026-08-01",
        updated_at=None,
        description="Description",
    )

def test_dashboard_requests_unfiltered_jobs(monkeypatch):
    mocked_get_jobs = Mock(return_value=[make_job()])

    monkeypatch.setattr(
        dashboard,
        "get_jobs",
        mocked_get_jobs,
    )

    dashboard.create_app()

    mocked_get_jobs.assert_called_once_with(
        filtered=False
    )

def test_dashboard_grid_contains_job(monkeypatch):
    monkeypatch.setattr(
        dashboard,
        "get_jobs",
        lambda **kwargs: [make_job()],
    )

    app = dashboard.create_app()

    grid = next(
        child
        for child in app.layout.children
        if getattr(child, "id", None) == "jobs-grid"
    )

    assert len(grid.rowData) == 1
    assert grid.rowData[0]["title"] == "Software Engineer"
    assert grid.rowData[0]["company"] == "Example"
    assert grid.rowData[0]["source"] == "greenhouse"