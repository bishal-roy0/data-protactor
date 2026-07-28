# API Reference

## `POST /analyze`

Checks supplied text and URLs for transparent baseline phishing, social-engineering, and suspicious-URL signals.

Sentinel AI does **not** open, visit, or execute the URLs in this milestone. This avoids making a submitted link trigger an outbound request from the API.

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
  "recommended_action": "block",
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
| `recommended_action` | `allow`, `show_caution`, or `block` |

## Current limitations

The current analyzer is rule-based and intentionally explainable. It does not replace human judgment, fetch URLs, perform malware scanning, or make claims about direct integration with third-party messaging platforms. OpenAI-assisted contextual analysis is planned for a later milestone.
