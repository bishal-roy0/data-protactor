# API Reference

## `POST /analyze`

Checks supplied text and URLs for transparent baseline phishing, social-engineering, and suspicious-URL signals.

Karna does **not** open, visit, download, crawl, or execute submitted URLs. This avoids making a submitted link trigger an unsafe request from the API.

### Request

Provide `text`, `urls`, or both. At least one is required.

```json
{
  "text": "Urgent: verify your account immediately with your OTP.",
  "urls": ["https://example.com"]
}
```

### Response

```json
{
  "risk_level": "critical",
  "risk_score": 80,
  "threat_category": "phishing",
  "evidence": [
    {
      "signal": "Credential request",
      "explanation": "Requests for passwords or verification codes can indicate an attempt to take over an account.",
      "weight": 35
    }
  ],
  "confidence": 0.85,
  "recommended_action": "quarantine",
  "summary": "Critical risk: 3 signal(s) require attention."
}
```

### Response fields

| Field | Meaning |
| --- | --- |
| `risk_level` | `safe`, `low`, `medium`, `high`, or `critical` |
| `risk_score` | A number from 0 to 100; higher means more suspicious signals were found |
| `threat_category` | The most likely detected concern |
| `evidence` | The exact signals that informed the result |
| `confidence` | The analyzer's confidence from 0 to 1 |
| `recommended_action` | `allow`, `show_caution`, `block`, or `quarantine` |
| `analysis_sources` | Non-sensitive capabilities used for the result, such as `local_rules` |

## `POST /analyze/image`

Accepts a single `image` multipart field. JPG, PNG, and WEBP are supported up to 5 MB. Karna validates the type and size in memory and does not persist uploads.

When `OPENAI_API_KEY` is configured, Karna can request an optional visual assessment for scam, fake-login, QR-risk, impersonation, and social-engineering cues. The image is sent to OpenAI only for that configured assessment; Karna does not persist the upload. Without the key, it returns a transparent fallback rather than claiming visual malware detection.

## `GET /config/public`

Returns only configuration that is safe for the public dashboard. At present it can return `android_app_download_url`, the HTTPS address of a real signed Android release. It never returns OpenAI, VirusTotal, or other secret values.

## Optional enrichment

When `VIRUSTOTAL_API_KEY` is configured, Karna can look up existing URL reputation data. It never opens, downloads, executes, or crawls submitted URLs.

## Fake-link analysis

Karna performs local structural checks for look-alike brand domains, encoded domains, IP-address URLs, misleading authority syntax, redirect and nested URLs, URL shorteners, credential-harvesting paths, payment lures, deceptive media links, and download indicators. A clean result means no current signals matched; it does not guarantee a link is safe.

## Current limitations

Karna is advisory and intentionally explainable. It does not replace human judgment, scan an entire device, remove malware, or directly integrate with third-party messaging platforms.
