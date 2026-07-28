# Security Policy

## Reporting a vulnerability

Please do not publish suspected security vulnerabilities in a public issue. Contact the repository owner privately with:

- a clear description of the issue
- steps to reproduce it
- the potential impact
- a suggested fix, if available

## API safety principles

- Never commit API keys or `.env` files.
- Karna does not fetch, open, download, or execute user-provided URLs in the baseline analyzer.
- Images are validated in memory and are not persisted by Karna.
- If optional OpenAI image analysis is enabled, uploaded image bytes are sent to OpenAI for that assessment; obtain appropriate authorization before enabling it.
- The API should not log submitted message content unless the deployment owner explicitly configures secure, privacy-aware logging.
- Risk assessments are advisory. Integrating platforms remain responsible for their moderation and enforcement decisions.
