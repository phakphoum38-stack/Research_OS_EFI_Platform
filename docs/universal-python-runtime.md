# Research OS EFI Platform — Universal Python + Runtime Architecture

Research OS EFI Platform is a standalone project. The separate Research OS project is reference/provenance only and is not a runtime dependency.

The repository keeps Windows, Linux, and macOS as separate execution domains. The universal layer provides contracts and orchestration only.

## Layers

1. Product discovery
   - read-only OS-specific discovery provider
   - manufacturer/product/board/BIOS identity
   - component inventory
2. Normalization
   - canonical text
   - PCI/USB identifier normalization
   - deterministic component ordering
3. Identity
   - product identity SHA
   - hardware configuration SHA
   - serial numbers and UUIDs are not required for the stable hashes
4. Platform registry
   - identifies the OS domain
   - records the owner runtime/discovery modules
   - never imports compatibility rules from another OS
5. Capability model
   - capability state is keyed by platform
   - Windows evidence cannot mutate macOS state
6. Product catalog
   - product records are distinct from observed machines
   - external/world datasets can be imported later with provenance
   - catalog data is owned by this project
7. Runtime
   - fixed, OS-owned read-only operations
   - no arbitrary shell execution API
   - local runtime refuses execution against another host OS
   - hardware mutation is disabled and not implemented
8. EFI research
   - candidate generation, OpenCore validation, preflight, and controlled experiment boundaries
   - EFI/ESP and firmware mutation remain explicitly outside the read-only runtime
9. Evidence
   - discovery output is wrapped in the existing EvidenceEnvelope
   - source pinning is explicit
   - unpinned local runs carry explicit development-source metadata
10. Flutter boundary
   - Flutter consumes JSON/contract outputs from the Python control plane
   - UI defines the product workflow; tests verify the UI after implementation
   - Flutter is not generated from test discovery

## Runtime isolation

Research OS EFI Platform Control Plane
        |
        +---- Windows discovery/runtime
        |
        +---- Linux discovery/runtime
        |
        +---- macOS discovery/runtime
        |
        +---- future platform adapters
        |
        +---- EFI research layer

Each adapter owns its commands and runtime evidence. There is no automatic cross-platform promotion of compatibility or runtime results.

## External research boundary

World/product research is implemented inside this project through project-owned adapters and provenance-aware ingestion. External observations are not automatically treated as truth or authority.

## Project boundary

Research OS EFI Platform and Research OS are separate projects:

    Research OS                    Research OS EFI Platform
    -----------                    ------------------------
    own code                       own code
    own runtime                    own runtime
    own data                       own data
    own evidence                   own evidence
                                   /
           -- architecture reference only --/

No cross-project runtime import, database sharing, service dependency, or combined product catalog is part of this architecture.

## Current evidence boundary

The universal foundation can inspect a real host when its OS adapter is available. CI uses fixtures and therefore does not prove any physical machine or OS compatibility. Product catalog population and global counts remain a separate sourced-data project.

## Safety

This layer never automates firmware, bootloader, ESP, BIOS, Secure Boot, storage-controller, or disk mutation.
