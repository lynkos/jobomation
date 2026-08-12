# Jobomation
Jobomation is a local-first tool for discovering, evaluating, and managing job opportunities.

> [!IMPORTANT]
> Jobomation is currently in early development. At present, only basic job collection is implemented.

## Requirements
- [x] Conda

## Installation
1. Clone repository, then change directory to `jobomation`
   ```sh
   git clone https://github.com/lynkos/jobomation.git && cd jobomation
   ```

2. Create Conda virtual environment (`job_env`)
   ```sh
   conda env create -f environment.yml
   ```

3. Activate Conda virtual environment (`job_env`)
   ```sh
   conda activate job_env
   ```

4. Install tests
   ```sh
   python -m pip install -e ".[dev]"
   ```

## Usage
Fetch job postings from [targets](config/targets.yml) and add to [SQLite database](data/jobomation.db)
   ```sh
   python -m jobomation.main
   ```

Run dashboard
   ```sh
   python -m jobomation.dashboard.app
   ```

## Testing
For everything:
   ```sh
   pytest -v
   ```

For one subsystem:
   ```sh
   pytest tests/test_models.py -v
   ```

## Miscellaneous
### TODOs
- [ ] Dashboard filter visibility
- [ ] Board synchronization / inactive detection
- [ ] More collectors:
  - [x] Indeed
  - [ ] Lever
  - [ ] LinkedIn
- [ ] Location + compensation filters
- [ ] Candidate profile
- [ ] LLM-based semantic scoring
- [ ] Ranking / inbox

### Design Doc
See [Design Doc](DESIGN.md) for more details.

### Database Schema
<div align="center"><img alt="SQLite database schema" src="assets/schema.svg"></div>

### Directory Tree
```text
.
├── .vscode/
│   └── settings.json
├── assets/
│   ├── pipeline.drawio
│   ├── pipeline.svg
│   ├── schema.drawio
│   └── schema.svg
├── config/
│   ├── filters.yml
│   └── targets.yml
├── data/
│   └── jobomation.db
├── src/
│   └── jobomation/
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── ashby.py
│       │   ├── greenhouse.py
│       │   ├── indeed.py
│       │   └── utils.py
│       ├── dashboard/
│       │   ├── __init__.py
│       │   └── app.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   ├── repository.py
│       │   └── schema.py
│       ├── filtering/
│       │   ├── __init__.py
│       │   └── rules.py
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       └── models.py
├── tests/
│   ├── conftest.py
│   ├── test_collectors.py
│   ├── test_config.py
│   ├── test_dashboard.py
│   ├── test_database.py
│   ├── test_filtering.py
│   ├── test_main.py
│   └── test_models.py
├── .gitignore
├── DESIGN.md
├── environment.yml
├── LICENSE.md
├── pyproject.toml
└── README.md
```