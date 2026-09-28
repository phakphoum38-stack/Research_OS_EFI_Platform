from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_sha(value: Mapping[str, Any]) -> str:
    encoded = (json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\\n").encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_fingerprint(*, source_id: str, locator: str, source_sha: str | None) -> str:
    return canonical_sha({"source_id": source_id, "locator": locator, "source_sha": source_sha})
