from jobomation import config

def test_load_targets(tmp_path, monkeypatch):
    targets_file = tmp_path / "targets.yml"

    targets_file.write_text(
        """
targets:
  - name: DoorDash
    source_type: greenhouse
    args:
      board: doordashusa

  - name: Ramp
    source_type: ashby
    args:
      board: ramp

  - name: Indeed - Software Engineer
    source_type: indeed
    args:
      search_term: software engineer
      location: United States
      results_wanted: 100
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "TARGETS_CONFIG_PATH",
        targets_file,
    )

    targets = config.load_targets()

    assert len(targets) == 3

    assert targets[0].name == "DoorDash"
    assert targets[0].source_type == "greenhouse"
    assert targets[0].args == {
        "board": "doordashusa",
    }

    assert targets[1].name == "Ramp"
    assert targets[1].source_type == "ashby"
    assert targets[1].args == {
        "board": "ramp",
    }

    assert targets[2].name == "Indeed - Software Engineer"
    assert targets[2].source_type == "indeed"
    assert targets[2].args == {
        "search_term": "software engineer",
        "location": "United States",
        "results_wanted": 100,
    }

def test_load_target_without_args(tmp_path, monkeypatch):
    targets_file = tmp_path / "targets.yml"

    targets_file.write_text(
        """
targets:
  - name: Example
    source_type: test
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "TARGETS_CONFIG_PATH",
        targets_file,
    )

    targets = config.load_targets()

    assert len(targets) == 1
    assert targets[0].args == {}

def test_load_filters(tmp_path, monkeypatch):
    filters_file = tmp_path / "filters.yml"

    filters_file.write_text(
        r"""
title:
  exclude:
    senior:
      - '\bsenior\b'
    principal:
      - '\bprincipal\b'
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "FILTERS_CONFIG_PATH",
        filters_file,
    )

    filters = config.load_filters()

    assert "title" in filters
    assert "exclude" in filters["title"]
    assert filters["title"]["exclude"]["senior"] == [
        r"\bsenior\b"
    ]

def test_load_empty_filters(tmp_path, monkeypatch):
    filters_file = tmp_path / "filters.yml"
    filters_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        config,
        "FILTERS_CONFIG_PATH",
        filters_file,
    )

    assert config.load_filters() == {}