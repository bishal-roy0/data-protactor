# Karna

Karna is a REST API and personal safety companion that helps authorized apps identify phishing, social-engineering, suspicious URLs, and unsafe attachments before a person acts. It is an integration-ready security layer, not a messaging application or device antivirus.

> **Project status:** baseline text, URL, and image analysis is available. Optional OpenAI vision and VirusTotal reputation enrichment require their own API keys.

## What Karna does

- Analyze text messages, URLs, and selected images
- Detect phishing and social-engineering attempts
- Return a threat score and clear explanation
- Recommend a safe next action

## Repository guide

Not sure where code belongs? See [Project Structure](docs/PROJECT_STRUCTURE.md). It maps each file to its purpose in plain language.

Read the endpoint contract in the [API Reference](docs/API_REFERENCE.md), and see [SECURITY.md](SECURITY.md) for reporting and deployment safety guidance.

For a visual explanation of each processing step and the code behind it, read [How Karna Works](docs/ARCHITECTURE.md).

For the future personal mobile-client pathway, read [Mobile Integration](docs/MOBILE_INTEGRATION.md).

For the Android Share Sheet companion setup and safe release process, read [Android Companion](docs/ANDROID_COMPANION.md).

Read [Accuracy and QA Report](docs/ACCURACY_AND_QA_REPORT.md) for reproducible baseline checks, live-dashboard evidence, known limitations, and the path to a measured accuracy benchmark.

Read [Production Accuracy Evaluation Report](docs/ACCURACY_EVALUATION_REPORT.md) for the versioned v1 corpus, category metrics, security checks, audit fixes, and live-test screenshots.

## Features in this milestone

- FastAPI application factory and OpenAPI documentation
- `GET /health` endpoint for service monitoring
- `POST /analyze` endpoint for baseline text and URL threat analysis
- Pydantic response schema
- Environment-based configuration
- Consistent fallback response for unexpected errors
- Automated health endpoint test
- Automated threat-analysis endpoint tests
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

- Safety dashboard: `http://127.0.0.1:8000/`
- Interactive documentation: `http://127.0.0.1:8000/docs`
- Health endpoint: `GET http://127.0.0.1:8000/health`
- Threat analysis: `POST http://127.0.0.1:8000/analyze`
- Image threat analysis: `POST http://127.0.0.1:8000/analyze/image`

Example response:

```json
{
  "status": "healthy",
  "service": "Karna",
  "environment": "development"
}
```

## Run tests

```powershell
$env:PYTHONPATH = "src"
pytest
```

## Optional API keys

`OPENAI_API_KEY` enables optional visual assessment for submitted images. `VIRUSTOTAL_API_KEY` enables an existing URL-reputation lookup. Both are optional: Karna continues to run its local, explainable analysis when either service is unavailable. Never commit real keys to GitHub.

`ANDROID_APP_DOWNLOAD_URL` is optional and public. Set it only after you have a tested, signed Android release; otherwise the dashboard keeps its Android download control disabled.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. It explains the project conventions, test command, and where each type of change belongs.

## Deploy to Render

This repository includes `render.yaml`. In Render, create a **Blueprint** from this GitHub repository and select the `main` branch. Render will install the dependencies, start the FastAPI service, and expose the dashboard and API through one public URL. The configured health check is `/health`.

## Deploy free with Vercel

For a personal or hackathon deployment, Vercel's free Hobby plan can deploy this FastAPI project directly from GitHub. Import this repository in Vercel and select the `main` branch. The included `src/index.py` entry point exposes the same dashboard and API without changing the application code.

## Safety boundary

Karna is advisory. It does not scan an entire device, remove malware, block phone downloads, intercept SMS, or access private messages without an authorized integration. See [Mobile Integration](docs/MOBILE_INTEGRATION.md) for the future mobile-client pathway.
