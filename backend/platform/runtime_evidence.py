from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .contracts import EvidenceEnvelope, verify_envelope
from .runtime import fingerprint


RESULTS = {"PASSED", "FAILED", "INCONCLUSIVE", "ABORTED"}
OBSERVATION_TYPES = {"system", "graphics", "storage", "network", "audio", "input", "boot", "other"}


@dataclass
class RuntimeObservation:
    type: str
    statement: str
    evidence_paths: list[str] = field(default_factory=list)
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        if self.type not in OBSERVATION_TYPES:
            raise ValueError("invalid observation type")
        if not self.statement.strip():
            raise ValueError("observation statement is required")


@dataclass
class RuntimeEvidence:
    schema_version: str
    case_id: str
    source_sha: str
    candidate_sha: str
    result: str
    platform: str
    observations: list[RuntimeObservation]
    artifacts: list[dict]
    human_controlled: bool = True
    hardware_mutation_performed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("unsupported runtime evidence schema")
        if not self.case_id or not self.source_sha or not self.candidate_sha:
            raise ValueError("case_id, source_sha and candidate_sha are required")
        if self.result not in RESULTS:
            raise ValueError("invalid runtime evidence result")
        if not self.platform.strip():
            raise ValueError("platform is required")
        if not self.human_controlled:
            raise ValueError("runtime evidence requires human-controlled execution")
        if self.hardware_mutation_performed:
            raise ValueError("hardware mutation cannot be recorded as an allowed runtime experiment")
        for observation in self.observations:
            observation.validate()

    def to_dict(self) -> dict:
        return asdict(self)


def collect_artifacts(paths: list[str]) -> list[dict]:
    records = []
    for raw in paths:
        path = Path(raw)
        if not path.is_file():
            raise FileNotFoundError(raw)
        records.append({"path": raw, "sha256": fingerprint(raw)})
    return records


def create_runtime_evidence(case_id: str, source_sha: str, candidate_sha: str,
                            result: str, platform: str,
                            observations: list[RuntimeObservation],
                            artifact_paths: list[str] | None = None) -> RuntimeEvidence:
    evidence = RuntimeEvidence(
        "1.0", case_id, source_sha, candidate_sha, result, platform,
        observations, collect_artifacts(artifact_paths or []),
    )
    evidence.validate()
    return evidence


def envelope_for_runtime(evidence: RuntimeEvidence) -> EvidenceEnvelope:
    evidence.validate()
    return EvidenceEnvelope.create(
        evidence.source_sha,
        "runtime-evidence",
        evidence.result,
        evidence.to_dict(),
        {"case_id": evidence.case_id, "candidate_sha": evidence.candidate_sha,
         "human_controlled": evidence.human_controlled},
    )


def write_runtime_evidence(evidence: RuntimeEvidence, output: str) -> None:
    envelope = envelope_for_runtime(evidence)
    Path(output).write_text(
        json.dumps(envelope.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_and_verify_runtime_evidence(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not verify_envelope(value):
        raise ValueError("invalid evidence envelope")
    if value.get("kind") != "runtime-evidence":
        raise ValueError("unexpected evidence kind")
    payload = value["payload"]
    evidence = RuntimeEvidence(
        payload["schema_version"], payload["case_id"], payload["source_sha"],
        payload["candidate_sha"], payload["result"], payload["platform"],
        [RuntimeObservation(**item) for item in payload["observations"]],
        payload["artifacts"], payload["human_controlled"],
        payload["hardware_mutation_performed"], payload["created_at"],
    )
    evidence.validate()
    if evidence.source_sha != value["source_sha"]:
        raise ValueError("source SHA mismatch")
    return value
