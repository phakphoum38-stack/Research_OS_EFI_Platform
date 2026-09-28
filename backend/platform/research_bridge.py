from dataclasses import asdict, dataclass

RESEARCH_OS_COMMIT = "c2abbae00acc596e94c7e75065823f413a94d699"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    name: str
    source_repo: str
    source_commit: str
    source_path: str
    source_symbol: str
    adaptation_reason: str
    target_component: str


DEFAULT_CAPABILITIES = (
    Capability(
        "evidence-manifest",
        "Immutable evidence ledger",
        "phakphoum38-stack/ENTERPRISE_API_ARCHITECTURE_LOGIC_TH",
        RESEARCH_OS_COMMIT,
        "tools/aeos_autobot_evidence_manifest.py",
        "SnapshotLock/build_manifest/verify_manifest",
        "Bind evidence to immutable source and digest.",
        "hackintosh.evidence",
    ),
    Capability(
        "wave-orchestrator",
        "Fail-closed research wave",
        "phakphoum38-stack/ENTERPRISE_API_ARCHITECTURE_LOGIC_TH",
        RESEARCH_OS_COMMIT,
        "tools/aeos_autobot_orchestrator.py",
        "run_wave/Job/WaveResult",
        "Reuse snapshot-lock semantics without hardware authority.",
        "hackintosh.orchestrator",
    ),
    Capability(
        "authority-boundary",
        "Human authority boundary",
        "phakphoum38-stack/ENTERPRISE_API_ARCHITECTURE_LOGIC_TH",
        RESEARCH_OS_COMMIT,
        "v3/research_os_v3/authority_boundary.py",
        "AuthorityBoundary.evaluate",
        "Separate preparation from authorization.",
        "hackintosh.authority",
    ),
)


def capability_report():
    capabilities = [asdict(item) for item in DEFAULT_CAPABILITIES]
    for item in capabilities:
        item["source_sha"] = item["source_commit"]
    return {
        "schema_version": "1.0",
        "bridge": "research-os-to-hackintosh",
        "source_policy": "PROVENANCE_REQUIRED",
        "capabilities": capabilities,
    }
