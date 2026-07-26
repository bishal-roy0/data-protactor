# Sentinel AI

Sentinel AI is a REST API that helps communication platforms identify phishing, social-engineering, and URL-based threats before content reaches users.

This repository currently contains the API foundation. Threat analysis and OpenAI integration will be added in later milestones.

## Features in this milestone

- FastAPI application factory and OpenAPI documentation
- `GET /health` endpoint for service monitoring
- Pydantic response schema
- Environment-based configuration
- Consistent fallback response for unexpected errors
- Automated health endpoint test

## Requirements

- Python 3.11 or later

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy the example environment file if you need local configuration:

```powershell
Copy-Item .env.example .env
```

## Run the API

```powershell
$env:PYTHONPATH = "src"
uvicorn sentinel_ai.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

- Interactive documentation: `http://127.0.0.1:8000/docs`
- Health endpoint: `GET http://127.0.0.1:8000/health`

Example response:

```json
{
  "status": "healthy",
  "service": "Sentinel AI",
  "environment": "development"
}
```

## Run tests

Install the test dependency, then run:

```powershell
python -m pip install pytest httpx
$env:PYTHONPATH = "src"
pytest
```

## Planned next milestone

Implement a validated `POST /analyze` contract for text and URLs, including structured threat scores, explanations, and recommended actions. OpenAI-powered analysis follows after that contract is in place.
