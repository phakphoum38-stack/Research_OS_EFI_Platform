from __future__ import annotations

import json
from pathlib import Path

from . import DiscoveryResult


def write_discovery_result(result: DiscoveryResult, output: str) -> None:
    Path(output).write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
