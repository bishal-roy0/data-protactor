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
- QR codes are decoded only in memory. Karna does not open or execute decoded destinations or non-web QR content.
- External datasets are kept outside the repository and are audited offline. Do not add submitted messages, QR images, datasets, or serialized third-party ML models to Git.
- If optional OpenAI image analysis is enabled, uploaded image bytes are sent to OpenAI for that assessment; obtain appropriate authorization before enabling it.
- The Android companion accepts only user-initiated Share Sheet content. Do not add background message collection or sensitive Android permissions without a separate privacy, platform-policy, and security review.
- GoPhish settings are optional and must be used only for owner-authorized simulation fixtures. The live API never calls GoPhish, launches campaigns, manages targets, or captures credentials.
- The API should not log submitted message content unless the deployment owner explicitly configures secure, privacy-aware logging.
- Risk assessments are advisory. Integrating platforms remain responsible for their moderation and enforcement decisions.
