# Research OS EFI Platform

Evidence-driven platform for researching real machines, EFI, and OS-specific capabilities.

**Project boundary:** Research OS EFI Platform is a standalone project. The separate Research OS project is not a runtime dependency, shared database, shared evidence store, or combined codebase. Architectural patterns may be referenced with provenance only.

The repository contains a universal Python research foundation while keeping Windows, Linux, and macOS as separate execution systems. The universal layer discovers product/hardware identity, normalizes device identifiers, tracks platform-scoped capabilities, catalogs known products, and provides read-only runtime adapters. It does not merge OS implementations.

## Current tracked machine

The first tracked hardware profile is ASUS Vivobook X1504VA / Intel Core i3-1315U.

The macOS domain remains conservative:

- Intel UHD 8086:A7A9 acceleration is not proven
- Intel VMD 8086:09AB / 8086:A77F storage path is not proven
- MT7902 Wi-Fi 14C3:7902 is not proven for macOS

## Universal Python + Runtime

The universal foundation is organized as:

    Product Discovery
        -> Product Identity
        -> Hardware Snapshot
        -> Platform-specific Runtime
        -> Evidence
        -> Platform-scoped Capability
        -> EFI Research

Windows, Linux, and macOS each own their discovery/runtime implementation. Compatibility decisions remain inside the corresponding OS domain.

The local runtime accepts only fixed, OS-owned operations. It has no arbitrary shell execution interface and refuses local execution against another host OS. Firmware, EFI/ESP, BIOS, Secure Boot, VMD, bootloader, and disk mutation are outside this runtime.

## Flutter boundary

Flutter remains the Control Center. Python exposes JSON contracts that the UI can consume; UI architecture is defined from the product workflow, not generated from tests. Flutter tests validate implemented behavior after the UI is designed.

## Project separation

- Research OS EFI Platform owns its own Python core, runtime, data, evidence, product catalog, and external adapters.
- Research OS remains a separate project.
- No Research OS module is imported as a runtime dependency.
- No Research OS database, runtime service, or external adapter is shared.
- Windows, Linux, and macOS remain separate platform domains inside this project.

## Run

    python -m unittest discover -s tests -v
    python -m backend.platform.cli platforms
    python -m backend.platform.cli discover-product discovery.json
    python -m backend.platform.cli runtime-operations
    python -m backend.platform.cli runtime-session runtime-session.json --case-id CASE --hardware-identity-sha SHA --operation os.version

See docs/universal-python-runtime.md for the layer-by-layer architecture.
