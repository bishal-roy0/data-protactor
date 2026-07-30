# GoPhish Simulation Boundary

Karna does **not** use GoPhish to decide whether a user-submitted URL is safe. GoPhish is an optional, owner-authorized phishing-simulation source for creating internal regression fixtures only.

## What the adapter does

`src/sentinel_ai/services/gophish_simulation.py` is intentionally separate from the API routes. It can read only HTTPS URLs from authorized GoPhish simulation metadata when all of these settings are present:

```text
GOPHISH_API_URL=
GOPHISH_API_KEY=
GOPHISH_SIMULATION_ENABLED=true
```

The adapter returns no data unless the owner explicitly enables it. It does not log or return campaign names, target data, credentials, raw provider errors, or API keys.

## What the adapter never does

- It is never called by `POST /analyze`.
- It does not send messages, launch campaigns, manage targets, capture credentials, or create phishing pages.
- It does not make a submitted user URL safer or more dangerous.
- It does not expose GoPhish information through Karna's public API.

Use GoPhish only in an authorized internal awareness-training environment. Karna's live detection relies on explainable local URL rules and optional reputation enrichment.
