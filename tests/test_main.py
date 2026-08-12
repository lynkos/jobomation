from jobomation.models import Target, Job
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

    target = Target(
        name="Example",
        source_type="test",
        args={
            "board": "example",
        },
    )

    def collector(*, board):
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
        "load_targets",
        lambda: [target],
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
        {
            "test": collector,
        },
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

def test_main_passes_target_args_to_collector(monkeypatch):
    received = {}

    target = Target(
        name="Indeed Test",
        source_type="test",
        args={
            "search_term": "software engineer",
            "location": "Boston, MA",
            "results_wanted": 100,
        },
    )

    def collector(**kwargs):
        received.update(kwargs)
        return []

    monkeypatch.setattr(
        main,
        "initialize_database",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "load_targets",
        lambda: [target],
    )

    monkeypatch.setattr(
        main,
        "load_filters",
        lambda: {},
    )

    monkeypatch.setattr(
        main,
        "COLLECTORS",
        {
            "test": collector,
        },
    )

    monkeypatch.setattr(
        main,
        "save_jobs",
        lambda jobs: None,
    )

    main.main()

    assert received == {
        "search_term": "software engineer",
        "location": "Boston, MA",
        "results_wanted": 100,
    }

def test_main_ignores_unknown_collector(monkeypatch, capsys):
    target = Target(
        name="Unknown",
        source_type="does-not-exist",
        args={},
    )

    monkeypatch.setattr(
        main,
        "initialize_database",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "load_targets",
        lambda: [target],
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

    assert (
        "Unsupported source type: does-not-exist"
        in output
    )

def test_main_continues_after_collector_failure(monkeypatch, capsys):
    bad_target = Target(
        name="Broken Source",
        source_type="broken",
        args={},
    )

    good_target = Target(
        name="Working Source",
        source_type="working",
        args={},
    )

    def broken_collector():
        raise RuntimeError("boom")

    def working_collector():
        return [make_job("Software Engineer")]

    saved = []

    monkeypatch.setattr(
        main,
        "initialize_database",
        lambda: None,
    )

    monkeypatch.setattr(
        main,
        "load_targets",
        lambda: [
            bad_target,
            good_target,
        ],
    )

    monkeypatch.setattr(
        main,
        "load_filters",
        lambda: {},
    )

    monkeypatch.setattr(
        main,
        "COLLECTORS",
        {
            "broken": broken_collector,
            "working": working_collector,
        },
    )

    monkeypatch.setattr(
        main,
        "save_jobs",
        lambda jobs: saved.extend(jobs),
    )

    main.main()

    output = capsys.readouterr().out

    assert "Failed to collect Broken Source" in output
    assert len(saved) == 1