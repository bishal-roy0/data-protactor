# Mobile Integration Pathway

Karna is an API that a future Android or iOS application can call after a user explicitly chooses to share content for analysis.

## Recommended personal-safety flow

1. A person copies a message or link, or chooses a screenshot in a future Karna mobile client.
2. The mobile client sends only that chosen item to Karna.
3. Karna returns an advisory result: `allow`, `show_caution`, `block`, or `quarantine`.
4. The mobile client explains the evidence and lets the person decide what to do.

Karna does not access private messages, intercept SMS, scan a phone, block device downloads, or remove malware. Those capabilities require a separately built native mobile app and explicit operating-system permissions.

## API example

```http
POST /analyze
Content-Type: application/json

{"text":"Urgent: verify your account with your OTP.","urls":[]}
```

For a screenshot, a mobile client can send a `multipart/form-data` request to `POST /analyze/image` with an `image` field. Karna accepts JPG, PNG, and WEBP images up to 5 MB.
