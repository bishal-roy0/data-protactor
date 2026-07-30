"""Create a local-only inventory of Karna evaluation datasets.

This tool never uploads, rewrites, or adds source data to the repository. It is
for provenance and label checks before a separately reviewed ML milestone.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def inspect_message_dataset(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows or {"Chat Log", "Result"} - set(rows[0]):
        raise ValueError("Message CSV must contain Chat Log and Result columns.")
    return {"file_name": path.name, "rows": len(rows), "labels": dict(sorted(Counter(row["Result"].strip() for row in rows).items())), "content_exported": False}


def inspect_qr_dataset(path: Path) -> dict[str, object]:
    files = [item for item in path.rglob("*") if item.is_file()]
    labels = Counter(item.parent.name for item in files)
    unexpected = sorted({item.suffix.casefold() for item in files if item.suffix.casefold() != ".png"})
    return {"directory_name": path.name, "files": len(files), "labels": dict(sorted(labels.items())), "unexpected_extensions": unexpected, "content_exported": False}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit local Karna datasets without copying content.")
    parser.add_argument("--messages", type=Path, required=True)
    parser.add_argument("--qr-directory", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"message_dataset": inspect_message_dataset(args.messages), "qr_dataset": inspect_qr_dataset(args.qr_directory)}, indent=2))


if __name__ == "__main__":
    main()
