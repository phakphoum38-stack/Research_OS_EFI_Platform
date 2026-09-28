from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse

from ..observations import ResearchObservation
from ..sources import ResearchSource


@dataclass(frozen=True)
class ResearchDocument:
    locator: str
    content: bytes
    title: str = ""
    source_type: str = "external"
    authority_scope: str = "research"
    retrieved_at: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def content_sha(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    def __post_init__(self) -> None:
        parsed = urlparse(self.locator)
        if not parsed.scheme:
            raise ValueError("locator must include a scheme")
        if not self.content:
            raise ValueError("content is required")


@dataclass(frozen=True)
class AdapterResult:
    source: ResearchSource
    document: ResearchDocument
    observations: tuple[ResearchObservation, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.to_dict(),
            "document": {
                "locator": self.document.locator,
                "title": self.document.title,
                "source_type": self.document.source_type,
                "authority_scope": self.document.authority_scope,
                "retrieved_at": self.document.retrieved_at,
                "content_sha": self.document.content_sha,
                "metadata": dict(self.document.metadata),
            },
            "observations": [item.to_dict() for item in self.observations],
        }


class ResearchAdapter(Protocol):
    name: str

    def fetch(self, locator: str) -> ResearchDocument:
        """Fetch one external research document without deciding whether it is true."""


def ingest_document(
    document: ResearchDocument,
    *,
    source_id: str,
    adapter_name: str,
    provenance: Mapping[str, Any] | None = None,
) -> AdapterResult:
    """Turn adapter output into a provenance-rich source record.

    Ingestion records what was retrieved. It deliberately does not create a
    supporting/contradicting observation because interpretation belongs to a
    research case or assessment step.
    """
    source = ResearchSource(
        source_id=source_id,
        source_type=document.source_type,
        locator=document.locator,
        retrieved_at=document.retrieved_at,
        source_sha=document.content_sha,
        authority_scope=document.authority_scope,
        provenance={
            "adapter": adapter_name,
            "document_metadata": dict(document.metadata),
            **dict(provenance or {}),
        },
    )
    return AdapterResult(source=source, document=document)
