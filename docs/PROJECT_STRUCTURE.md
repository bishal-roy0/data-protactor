# Project Structure

This guide explains where each part of Karna lives. Start here if you are new to the project.

```text
data-protactor/
├── .github/workflows/ci.yml        # Automated GitHub test workflow
├── docs/                           # Plain-language project documentation
├── src/sentinel_ai/                # Application source code
│   ├── main.py                     # Starts and configures the FastAPI application
│   ├── api/                        # HTTP endpoints and their JSON models
│   │   ├── routes.py               # URL paths such as /health and future /analyze
│   │   └── schemas.py              # Defines the JSON fields returned by the API
│   └── core/                       # Shared application behaviour
│       ├── config.py               # Reads configuration from environment variables
│       └── errors.py               # Provides safe responses for server errors
├── tests/                          # Automated checks for API behaviour
├── .env.example                    # Example local configuration; contains no secrets
├── requirements.txt                # Packages required to run the API
├── requirements-dev.txt            # Extra packages required to run tests
└── README.md                       # Project overview and setup instructions
```

The Android companion lives in `android/app/`: `MainActivity.kt` receives Android Share Sheet content, `share/` validates it, `data/` calls the Karna API, and `ui/` displays the review and advisory result.

## Where to make common changes

| If you want to... | Edit this file or folder |
| --- | --- |
| Add or change an API URL | `src/sentinel_ai/api/routes.py` |
| Change a request or response JSON field | `src/sentinel_ai/api/schemas.py` |
| Change application settings | `src/sentinel_ai/core/config.py` and `.env.example` |
| Change how startup is configured | `src/sentinel_ai/main.py` |
| Change public branding or optional API keys | `src/sentinel_ai/core/config.py` and `.env.example` |
| Change URL reputation behavior | `src/sentinel_ai/services/reputation.py` |
| Change image-analysis behavior | `src/sentinel_ai/services/image_analyzer.py` |
| Change Android Share Sheet handling | `android/app/src/main/java/com/karna/companion/share/` |
| Add a test | `tests/` |
| Explain a project decision | `docs/` |
| Change packages used by the running API | `requirements.txt` |

## Important safety notes

- Never commit a real `.env` file or API key. Use `.env.example` only as a template.
- Keep threat-analysis logic separate from HTTP route definitions. Routes accept requests and return responses; analysis services contain the security decisions.
- Add a matching test whenever an endpoint or response model changes.
