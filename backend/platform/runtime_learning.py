from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .research_case import ResearchCase
from .runtime_evidence import load_and_verify_runtime_evidence


@dataclass(frozen=True)
class KnowledgeObservation:
    case_id: str
    evidence_id: str
    result: str
    platform: str
    observation_type: str
    statement: str
    evidence_paths: tuple[str, ...] = ()
    source_sha: str = ""
    candidate_sha: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "result": self.result,
            "platform": self.platform,
            "observation_type": self.observation_type,
            "statement": self.statement,
            "evidence_paths": list(self.evidence_paths),
            "source_sha": self.source_sha,
            "candidate_sha": self.candidate_sha,
        }


@dataclass
class ResearchKnowledge:
    observations: list[KnowledgeObservation] = field(default_factory=list)

    def add_runtime_evidence(self, envelope: dict[str, Any]) -> list[KnowledgeObservation]:
        payload = envelope["payload"]
        evidence_id = envelope["evidence_id"]
        created = [
            KnowledgeObservation(
                case_id=payload["case_id"],
                evidence_id=evidence_id,
                result=payload["result"],
                platform=payload["platform"],
                observation_type=item["type"],
                statement=item["statement"],
                evidence_paths=tuple(item.get("evidence_paths", [])),
                source_sha=payload["source_sha"],
                candidate_sha=payload["candidate_sha"],
            )
            for item in payload["observations"]
        ]
        self.observations.extend(created)
        return created

    def for_case(self, case_id: str) -> list[KnowledgeObservation]:
        return [item for item in self.observations if item.case_id == case_id]

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": "1.0", "observations": [item.to_dict() for item in self.observations]}


def learn_from_runtime_evidence(case: ResearchCase, evidence_path: str) -> tuple[ResearchCase, ResearchKnowledge]:
    envelope = load_and_verify_runtime_evidence(evidence_path)
    payload = envelope["payload"]
    if payload["case_id"] != case.case_id:
        raise ValueError("runtime evidence case_id mismatch")
    if payload["source_sha"] != case.source_sha:
        raise ValueError("runtime evidence source SHA mismatch")

    knowledge = ResearchKnowledge()
    learned = knowledge.add_runtime_evidence(envelope)
    updated = ResearchCase(
        case.case_id,
        case.source_sha,
        case.profile,
        case.hypothesis,
        case.facts,
        case.observations + tuple(item.to_dict() for item in learned),
        case.provenance + ({"evidence_id": envelope["evidence_id"], "kind": "runtime-evidence"},),
    )
    return updated, knowledge
