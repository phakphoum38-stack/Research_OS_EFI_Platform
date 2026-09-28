# Hackintosh AI Platform — Long-term architecture

The platform is an evidence-driven research and generation system for real hardware. It must distinguish observed hardware identity from macOS runtime proof.

## Layers

1. Evidence — Windows hardware, PCI/USB IDs, ACPI tables, OpenCore artifacts, and macOS runtime evidence.
2. Python core — parsing, topology extraction, compatibility reasoning, manifest hashing, candidate generation, and validation.
3. Flutter Control Center — human-facing exploration and experiment control. It does not silently modify firmware or the Windows boot path.
4. OpenCore artifacts — generated candidates are versioned, inspectable, and gated before any boot experiment.
5. Runtime feedback — successful or failed boot experiments become new evidence rather than assumptions.

## Evidence state machine

UNKNOWN → OBSERVED → FIRMWARE_PROVEN → OS_PROVEN → MACOS_PROVEN → RUNTIME_PROVEN

BLOCKED is orthogonal: a component can be blocked while another component continues to be researched.

## X1504VA first-class topology

The initial profile records Intel UHD 8086:A7A9, Intel VMD 8086:09AB/A77F, KIOXIA KBG60ZNS512G, Realtek ALC256 10EC:0256, MediaTek MT7902 14C3:7902, Bluetooth 13D3:3579, and ASUS touchpad ASUF1300.

## Safety boundaries

- Never change BIOS settings automatically.
- Never overwrite the Windows EFI system partition automatically.
- Never claim an EFI is bootable solely because a plist validates.
- Every generated candidate receives a manifest and source fingerprint.
- Runtime experiments are explicit and recorded.
