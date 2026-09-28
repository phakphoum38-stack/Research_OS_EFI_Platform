from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .base import RuntimeContext, RuntimeResult
from .manager import RuntimeManager


@dataclass
class RuntimeSession:
    platform: str
    results: list[RuntimeResult] = field(default_factory=list)
    stopped_on_failure: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "platform": self.platform,
            "results": [item.to_dict() for item in self.results],
            "stopped_on_failure": self.stopped_on_failure,
        }


class RuntimeEngine:
    def __init__(self, manager: RuntimeManager | None = None) -> None:
        self.manager = manager or RuntimeManager()

    def run(
        self,
        platform: str,
        operation_ids: Iterable[str],
        *,
        fail_closed: bool = True,
        context: RuntimeContext | None = None,
    ) -> RuntimeSession:
        session = RuntimeSession(platform)
        target_context = context or RuntimeContext(
            platform=self.manager.adapter(platform).platform
        )
        for operation_id in operation_ids:
            result = self.manager.execute(
                platform, operation_id, context=target_context
            )
            session.results.append(result)
            if result.returncode != 0 and fail_closed:
                session.stopped_on_failure = True
                break
        return session