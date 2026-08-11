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

## Usage
Fetch job postings from Greenhouse and add to [SQLite Database](data/jobomation.db)
   ```sh
   python -m jobomation.main
   ```

Run dashboard
    ```sh
    python -m jobomation.dashboard.app
    ```

## Miscellaneous
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
├── data/
│   └── jobomation.db
├── src/
│   └── jobomation/
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── ashby.py
│       │   └── greenhouse.py
│       ├── dashboard/
│       │   ├── __init__.py
│       │   └── app.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   ├── repository.py
│       │   └── schema.py
│       ├── __init__.py
│       ├── main.py
│       └── models.py
├── .gitignore
├── DESIGN.md
├── environment.yml
├── LICENSE.md
├── pyproject.toml
└── README.md
```