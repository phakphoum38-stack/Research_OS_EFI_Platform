from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evidence import EvidenceLevel
from .runtime_evidence import load_and_verify_runtime_evidence


PROMOTION_RULES = {
    ("macOS", "graphics", "Intel UHD 8086:A7A9 acceleration verified"): (
        "gpu", "8086:A7A9", EvidenceLevel.MACOS_PROVEN
    ),
    ("macOS", "storage", "Intel VMD 8086:09AB/A77F storage path verified"): (
        "storage.vmd", "8086:09AB,8086:A77F", EvidenceLevel.MACOS_PROVEN
    ),
}


@dataclass(frozen=True)
class CompatibilityDecision:
    component: str
    value: str
    level: EvidenceLevel
    evidence_id: str
    case_id: str
    source_sha: str
    candidate_sha: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "value": self.value,
            "level": self.level.value,
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "source_sha": self.source_sha,
            "candidate_sha": self.candidate_sha,
            "reason": self.reason,
        }


def compatibility_decisions_from_runtime_evidence(
    evidence_path: str,
) -> list[CompatibilityDecision]:
    envelope = load_and_verify_runtime_evidence(evidence_path)
    payload = envelope["payload"]
    if payload["result"] != "PASSED" or payload["platform"].strip().lower() != "macos":
        return []

    decisions: list[CompatibilityDecision] = []
    for observation in payload["observations"]:
        key = (
            payload["platform"],
            observation["type"],
            observation["statement"].strip(),
        )
        rule = PROMOTION_RULES.get(key)
        if not rule:
            continue
        component, value, level = rule
        decisions.append(
            CompatibilityDecision(
                component, value, level, envelope["evidence_id"],
                payload["case_id"], payload["source_sha"], payload["candidate_sha"],
                "explicit controlled runtime promotion rule",
            )
        )
    return decisions
