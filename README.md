# Hackintosh AI Platform

Evidence-driven platform for researching Hackintosh compatibility and generating EFI candidates on Windows.

## Current target

The first tracked hardware profile is **ASUS Vivobook X1504VA / Intel Core i3-1315U**.

The repository now uses a conservative compatibility gate:

- hardware identity is recorded separately from macOS support
- unsupported or unresolved devices are not converted into guessed kexts
- EFI generation is blocked while critical GPU/storage evidence is unresolved
- generated plist data uses real XML plist serialization
- CI publishes an inspectable compatibility report

Current X1504VA blockers:

- Intel UHD `8086:A7A9` acceleration is not proven
- Intel VMD `8086:09AB` / `8086:A77F` storage path is not proven

MT7902 Wi-Fi (`14C3:7902`) is also currently treated as unproven for macOS.

See `docs/x1504va-compatibility.md` and `hardware/x1504va.json`.

## Important boundary

A compatibility report or generated plist candidate is **not** proof of a bootable Hackintosh. Real hardware boot evidence is tracked separately.

## Run

    python -m unittest discover -s tests -v

The repository's GitHub Actions workflow runs the same compatibility gate on pull requests and pushes to `main`.
