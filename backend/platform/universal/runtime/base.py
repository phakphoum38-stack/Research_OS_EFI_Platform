from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from ..platforms import PlatformId, normalize_platform


class RuntimeMode(str, Enum):
    LOCAL = "local"


class RuntimeSafetyError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeOperation:
    operation_id: str
    argv: tuple[str, ...]
    timeout_seconds: int = 60
    mutates_hardware: bool = False


@dataclass(frozen=True)
class RuntimeContext:
    platform: PlatformId
    mode: RuntimeMode = RuntimeMode.LOCAL
    allow_mutation: bool = False


@dataclass(frozen=True)
class RuntimeResult:
    operation_id: str
    platform: PlatformId
    started_at: str
    finished_at: str
    returncode: int
    stdout: str
    stderr: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "operation_id": self.operation_id,
            "platform": self.platform.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class RuntimeAdapter(ABC):
    platform: PlatformId

    @abstractmethod
    def operations(self) -> dict[str, RuntimeOperation]:
        raise NotImplementedError

    def execute(self, operation_id: str, context: RuntimeContext) -> RuntimeResult:
        if context.platform != self.platform:
            raise RuntimeSafetyError(
                f"cross-platform runtime denied: {context.platform.value} -> {self.platform.value}"
            )
        operation = self.operations().get(operation_id)
        if operation is None:
            raise KeyError(f"unsupported runtime operation: {operation_id}")
        if operation.mutates_hardware and not context.allow_mutation:
            raise RuntimeSafetyError("hardware mutation is disabled")
        if operation.mutates_hardware:
            raise RuntimeSafetyError("hardware mutation runtime is not implemented")

        started = datetime.now(timezone.utc).isoformat()
        try:
            result = subprocess.run(
                list(operation.argv),
                capture_output=True,
                text=True,
                timeout=operation.timeout_seconds,
                check=False,
            )
            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or "runtime operation timed out"
            returncode = 124
        finished = datetime.now(timezone.utc).isoformat()
        return RuntimeResult(
            operation.operation_id,
            normalize_platform(context.platform),
            started,
            finished,
            returncode,
            stdout,
            stderr,
        )