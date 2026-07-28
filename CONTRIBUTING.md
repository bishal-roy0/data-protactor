# Contributing to Sentinel AI

## Before you make a change

1. Read [the project structure guide](docs/PROJECT_STRUCTURE.md) to find the correct file.
2. Keep each change focused on one purpose.
3. Do not commit `.env` files, API keys, or other secrets.

## Local development

Install Python 3.11 or later, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = "src"
pytest
```

Start the API locally with:

```powershell
$env:PYTHONPATH = "src"
uvicorn sentinel_ai.main:app --reload
```

## Code expectations

- Use clear names and typed Pydantic models for API data.
- Put endpoints in `src/sentinel_ai/api/routes.py`.
- Put shared configuration and infrastructure in `src/sentinel_ai/core/`.
- Add or update tests in `tests/` with every behavior change.
- Use professional, focused commit messages, for example: `feat(api): add threat analysis request model`.
