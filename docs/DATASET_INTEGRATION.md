# Dataset integration and safety boundary

Karna uses the following user-supplied datasets as an **offline evaluation and rule-review input**. They are not copied into this repository, uploaded by the API, or read during a user scan.

| Source | Local purpose | Current verified shape |
| --- | --- | --- |
| `emotional_social_engineering_attacks.csv` | Review message-manipulation examples and false-positive cases | 82 rows: 50 `Attack`, 32 `No Attack` |
| `Multi-version QR codes dataset/` | Validate QR input handling against benign and malicious labels | 700 PNG files in `benign` and `malicious` folders |
| `vaibhavbichave/Phishing-URL-Detection` | Review local URL-structure feature ideas | External reference only; its bundled model and data are not redistributed |

## Why the linked phishing project is not embedded

The referenced implementation fetches submitted URLs, page content, WHOIS records, rank data, and search results. Karna deliberately does none of those operations: a submitted link must never cause Karna to visit, download, crawl, or execute a destination. Its serialized `model.pkl` is also not loaded because untrusted pickle files are unsafe to deserialize and its training provenance has not been independently reviewed.

Karna instead implements independently written, explainable, local checks for the safe structural concepts: IP-address hosts, encoded domains, redirect parameters, shortened links, deceptive look-alike domains, reward lures, credential paths, and download indicators. The external project remains a research reference, not a runtime dependency. See the upstream [repository](https://github.com/vaibhavbichave/Phishing-URL-Detection) and its feature implementation for source context.

## Offline audit command

Run this command on a computer that contains the datasets. It only prints counts and labels; it never exports messages, QR images, or URLs.

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe scripts\audit_external_datasets.py `
  --messages "E:\Dataset\emotional_social_engineering_attacks.csv" `
  --qr-directory "E:\Dataset\Multi-version QR codes dataset"
```

## Runtime behavior

- Text scans use conservative rules from reviewed patterns. Emotional language alone is not flagged; it must be combined with a risky request such as identity verification or sharing access.
- `POST /analyze/qr` accepts a user-provided JPG, PNG, or WEBP up to 5 MB. It decodes the QR content only in memory.
- If a QR code contains an HTTP(S) URL, Karna passes the text to the existing local URL analyzer. It never opens the destination.
- QR content that is not a web URL is never executed, imported, or passed to another app. Karna returns a caution result.
- A no-match or unreadable result is not proof that the QR code is safe.

## Future ML milestone

Do not train or publish accuracy claims from these sources alone. First record licensing/provenance, split data by source to prevent leakage, create a held-out multilingual test set, have labels reviewed by at least two people, and publish precision, recall, F1, false-positive rate, and sample sizes. Any future model must be stored in a safe, versioned format and must use features that preserve Karna's no-crawl boundary.
