from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .evidence import EvidenceManifest


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(profile: Mapping[str, Any], sources: list[str] | None = None) -> dict[str, Any]:
    manifest = EvidenceManifest.from_profile(profile).to_dict()
    manifest["sources"] = []
    for source in sources or []:
        path = Path(source)
        item: dict[str, Any] = {"path": str(path)}
        if path.is_file():
            item["sha256"] = sha256_file(path)
            item["size"] = path.stat().st_size
        manifest["sources"].append(item)
    return manifest


def write_manifest(profile_path: str, output_path: str, sources: list[str] | None = None) -> None:
    with open(profile_path, encoding="utf-8") as handle:
        profile = json.load(handle)
    manifest = build_manifest(profile, sources)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\\n")
