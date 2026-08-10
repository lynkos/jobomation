# Jobomation
See [Design Doc](DESIGN.md) for more details.

## Requirements
- [x] Conda

## Installation
1. Install dependencies
   ```sh
   conda env create -f environment.yml
   conda activate job_env
   pip install -e .
   ```

## Directory Tree
```text
jobomation/
├── README.md
├── pyproject.toml
├── environment.yml
├── .env.example
├── .gitignore
├── config/
│   ├── companies.yaml
│   └── candidate.yaml
├── data/
│   └── .gitkeep
├── scripts/
│   ├── collect.py
│   ├── evaluate.py
│   └── run_dashboard.py
├── src/
│   └── jobomation/
│       ├── __init__.py
│       ├── config.py
│       ├── models.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   ├── schema.py
│       │   └── repository.py
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── greenhouse.py
│       │   └── lever.py
│       ├── normalization/
│       │   ├── __init__.py
│       │   └── normalize.py
│       ├── filtering/
│       │   ├── __init__.py
│       │   └── rules.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── evaluator.py
│       │   └── prompts.py
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── ollama.py
│       ├── ranking/
│       │   ├── __init__.py
│       │   └── ranker.py
│       └── dashboard/
│           ├── __init__.py
│           └── app.py
└── tests/
    ├── test_normalization.py
    ├── test_filtering.py
    └── fixtures/
```