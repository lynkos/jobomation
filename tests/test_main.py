from jobomation.models import Company, Job
from jobomation import main

def make_job(title: str) -> Job:
    return Job(
        source="greenhouse",
        source_job_id="123",
        title=title,
        company="Example",
        location="Boston",
        url="https://example.com",
        first_published="2026-08-01",
        updated_at=None,
        description="Description",
    )

def test_main_collects_filters_and_saves(monkeypatch):
    initialized = []
    saved = []

    company = Company(
        name="Example",
        source_type="test",
        board_id="example",
    )

    def collector(board):
        assert board == "example"

        return [
            make_job("Software Engineer"),
            make_job("Senior Software Engineer"),
        ]

    monkeypatch.setattr(
        main,
        "initialize_database",
        lambda: initialized.append(True),
    )

    monkeypatch.setattr(
        main,
        "load_companies",
        lambda: [company],
    )

    monkeypatch.setattr(
        main,
        "load_filters",
        lambda: {
            "title": {
                "exclude": {
                    "senior": [r"\bsenior\b"],
                }
            }
        },
    )

    monkeypatch.setattr(
        main,
        "COLLECTORS",
        {"test": collector},
    )

    monkeypatch.setattr(
        main,
        "save_jobs",
        lambda jobs: saved.extend(jobs),
    )

    main.main()

    assert initialized == [True]
    assert len(saved) == 2

    assert saved[0].filtered is False

    assert saved[1].filtered is True
    assert saved[1].filter_reason == "title:senior"

def test_main_ignores_unknown_collector(monkeypatch, capsys):
    company = Company(
        name="Unknown",
        source_type="does-not-exist",
        board_id="unknown",
    )

    monkeypatch.setattr(
        main,
        "initialize_database",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "load_companies",
        lambda: [company],
    )

    monkeypatch.setattr(
        main,
        "load_filters",
        lambda: {},
    )

    monkeypatch.setattr(
        main,
        "COLLECTORS",
        {},
    )

    main.main()

    output = capsys.readouterr().out

    assert "Unsupported source type: does-not-exist" in output