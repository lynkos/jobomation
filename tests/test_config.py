from jobomation import config

def test_load_companies(tmp_path, monkeypatch):
    companies_file = tmp_path / "companies.yml"

    companies_file.write_text(
        """
companies:
  - name: DoorDash
    source_type: greenhouse
    board_id: doordashusa

  - name: Ramp
    source_type: ashby
    board_id: ramp
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        config,
        "COMPANIES_CONFIG_PATH",
        companies_file,
    )

    companies = config.load_companies()

    assert len(companies) == 2

    assert companies[0].name == "DoorDash"
    assert companies[0].source_type == "greenhouse"
    assert companies[0].board_id == "doordashusa"

    assert companies[1].name == "Ramp"
    assert companies[1].source_type == "ashby"
    assert companies[1].board_id == "ramp"

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