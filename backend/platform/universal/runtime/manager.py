from __future__ import annotations

from .base import RuntimeAdapter, RuntimeContext, RuntimeSafetyError, RuntimeResult
from .linux import LinuxRuntime
from .macos import MacOSRuntime
from .windows import WindowsRuntime
from ..platforms import PlatformId, normalize_platform


_ADAPTERS = {
    PlatformId.WINDOWS: WindowsRuntime,
    PlatformId.LINUX: LinuxRuntime,
    PlatformId.MACOS: MacOSRuntime,
}


class RuntimeManager:
    def adapter(self, platform: str | PlatformId) -> RuntimeAdapter:
        target = normalize_platform(platform)
        adapter_type = _ADAPTERS.get(target)
        if adapter_type is None:
            raise RuntimeSafetyError(f"no local runtime adapter registered for {target.value}")
        return adapter_type()

    def execute(
        self,
        platform: str | PlatformId,
        operation_id: str,
        *,
        context: RuntimeContext | None = None,
    ) -> RuntimeResult:
        target = normalize_platform(platform)
        runtime_context = context or RuntimeContext(platform=target)
        if runtime_context.platform != target:
            raise RuntimeSafetyError("runtime context platform mismatch")
        return self.adapter(target).execute(operation_id, runtime_context)

    def operations(self, platform: str | PlatformId) -> list[str]:
        return sorted(self.adapter(platform).operations())