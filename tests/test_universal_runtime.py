import unittest

from backend.platform.universal.platforms import PlatformId
from backend.platform.universal.runtime.base import RuntimeContext, RuntimeSafetyError
from backend.platform.universal.runtime.manager import RuntimeManager


class UniversalRuntimeTests(unittest.TestCase):
    def test_windows_adapter_is_platform_specific(self):
        manager = RuntimeManager()
        self.assertIn("os.version", manager.operations(PlatformId.WINDOWS))
        with self.assertRaises(RuntimeSafetyError):
            manager.execute(
                PlatformId.WINDOWS,
                "os.version",
                context=RuntimeContext(platform=PlatformId.LINUX),
            )

    def test_linux_and_macos_are_separate_adapters(self):
        manager = RuntimeManager()
        self.assertIn("hardware.pci", manager.operations(PlatformId.LINUX))
        self.assertIn("hardware.pci", manager.operations(PlatformId.MACOS))

    def test_local_execution_rejects_non_host_os(self):
        manager = RuntimeManager()
        other = PlatformId.MACOS if manager.adapter(PlatformId.WINDOWS).platform == PlatformId.WINDOWS else PlatformId.WINDOWS
        with self.assertRaises(RuntimeSafetyError):
            manager.execute(other, "os.version")


if __name__ == "__main__":
    unittest.main()
