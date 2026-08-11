# Jobomation
Jobomation is a local-first tool for discovering, evaluating, and managing job opportunities.

> [!IMPORTANT]
> Jobomation is currently in early development. At present, only basic job collection is implemented.

## Requirements
- [x] Conda

## Installation
1. Clone repository
   ```sh
   git clone https://github.com/lynkos/jobomation.git
   cd jobomation
   ```

2. Create and activate Conda environment (`job_env`)
   ```sh
   conda env create -f environment.yml
   conda activate job_env
   ```

## Usage
Fetch and display job postings from Greenhouse
   ```sh
   python -m jobomation.collectors.greenhouse
   ```

## Miscellaneous
### Design Doc
See [Design Doc](DESIGN.md) for more details.

### Directory Tree
```text
.
├── .vscode/
│   └── settings.json
├── assets/
│   ├── pipeline.drawio
│   └── pipeline.svg
├── config/
│   └── profile.json
├── data/
│   └── jobomation.db
├── src/
│   └── jobomation/
│       ├── __init__.py
│       ├── models.py
│       └── collectors/
│           ├── __init__.py
│           └── greenhouse.py
├── .gitignore
├── DESIGN.md
├── environment.yml
├── LICENSE.md
├── pyproject.toml
└── README.md
```