from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .knowledge import CompatibilityKnowledge
from .validator import validate_candidate

REQUIRED_EXPERIMENT_FIELDS = ("hypothesis", "candidate_sha", "status")


def build_preflight(
    profile: Mapping[str, Any],
    candidate_root: str,
    experiment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a non-mutating M10 preflight decision.

    This function never changes firmware, ESP, Secure Boot, VMD, disks, or BCD.
    A result of READY_FOR_HUMAN_BOOT means only that repository-side checks
    passed; it is not authorization to boot or proof that macOS will work.
    """
    validation = validate_candidate(candidate_root)
    knowledge = CompatibilityKnowledge.from_profile(profile)
    blockers = [
        f"{fact.component}:{fact.value} remains unresolved"
        for fact in knowledge.unresolved()
    ]

    if experiment is None:
        blockers.append("experiment record is required")
    else:
        for field in REQUIRED_EXPERIMENT_FIELDS:
            if not experiment.get(field):
                blockers.append(f"experiment field '{field}' is required")

    report_path = Path(candidate_root) / "OC" / "compatibility-report.json"
    report: dict[str, Any] = {}
    if report_path.is_file():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            blockers.append("compatibility-report.json is invalid JSON")
    else:
        blockers.append("compatibility-report.json is missing")

    if validation["status"] != "PASS":
        blockers.extend(validation["errors"])

    if report.get("status") not in {"READY", "PASS"}:
        blockers.append(
            f"compatibility report status is {report.get('status', 'MISSING')}"
        )

    status = "BLOCKED" if blockers else "READY_FOR_HUMAN_BOOT"
    return {
        "schema_version": "1.0",
        "status": status,
        "human_action_required": status == "READY_FOR_HUMAN_BOOT",
        "mutation_performed": False,
        "blockers": blockers,
        "warnings": validation["warnings"],
        "experiment": dict(experiment) if experiment else None,
    }


def write_preflight(result: Mapping[str, Any], output: str) -> None:
    Path(output).write_text(
        json.dumps(dict(result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
