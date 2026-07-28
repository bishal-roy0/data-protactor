# Sentinel AI

Sentinel AI is a REST API that helps communication platforms identify phishing, social-engineering, and URL-based threats before content reaches users. It is an integration-ready security layer, not a messaging application.

> **Project status:** API foundation complete. Threat-analysis endpoints and OpenAI integration are planned next.

## What Sentinel AI will do

- Analyze text messages and URLs
- Detect phishing and social-engineering attempts
- Return a threat score and clear explanation
- Recommend a safe next action

## Repository guide

Not sure where code belongs? See [Project Structure](docs/PROJECT_STRUCTURE.md). It maps each file to its purpose in plain language.

## Features in this milestone

- FastAPI application factory and OpenAPI documentation
- `GET /health` endpoint for service monitoring
- Pydantic response schema
- Environment-based configuration
- Consistent fallback response for unexpected errors
- Automated health endpoint test
- GitHub Actions workflow that runs tests on pushes and pull requests

## Requirements

- Python 3.11 or later

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
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

```powershell
$env:PYTHONPATH = "src"
pytest
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. It explains the project conventions, test command, and where each type of change belongs.

## Planned next milestone

Implement a validated `POST /analyze` contract for text and URLs, including structured threat scores, explanations, and recommended actions. OpenAI-powered analysis follows after that contract is in place.
