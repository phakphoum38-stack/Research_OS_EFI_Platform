from __future__ import annotations

from urllib.request import Request, urlopen

from .base import ResearchDocument


class HttpResearchAdapter:
    """Small stdlib HTTP adapter; callers remain responsible for interpretation."""

    name = "http"

    def __init__(self, *, timeout: float = 15.0, user_agent: str = "Research-OS-EFI-Platform/1.0") -> None:
        if timeout <= 0:
            raise ValueError("timeout must be > 0")
        self.timeout = timeout
        self.user_agent = user_agent

    def fetch(self, locator: str) -> ResearchDocument:
        request = Request(locator, headers={"User-Agent": self.user_agent})
        with urlopen(request, timeout=self.timeout) as response:
            content = response.read()
            content_type = response.headers.get("Content-Type", "")
            retrieved_at = response.headers.get("Date", "")
        return ResearchDocument(
            locator=locator,
            content=content,
            source_type="external_http",
            retrieved_at=retrieved_at,
            metadata={"content_type": content_type},
        )
