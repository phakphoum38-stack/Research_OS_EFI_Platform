# Research OS to Hackintosh EFI Platform Bridge

The bridge reuses proven Research OS patterns while preserving the Hackintosh safety boundary.

Research OS source commit: c2abbae00acc596e94c7e75065823f413a94d699.

Reused capabilities:
- immutable evidence manifest: tools/aeos_autobot_evidence_manifest.py
- fail-closed wave orchestration: tools/aeos_autobot_orchestrator.py
- authority boundary: v3/research_os_v3/authority_boundary.py

Lifecycle:
COLLECT -> NORMALIZE -> REASON -> BUILD_CANDIDATE -> VALIDATE -> PREFLIGHT -> HUMAN_EXPERIMENT -> OBSERVE -> EVIDENCE -> LEARN

GPU 8086:A7A9 and VMD 8086:09AB/A77F remain RESEARCH until macOS runtime evidence exists. READY_FOR_HUMAN_BOOT is repository-side only. No BIOS, ESP, Secure Boot, VMD, disk, firmware, or bootloader mutation is authorized by this platform.
