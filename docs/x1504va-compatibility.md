# X1504VA compatibility evidence

Target: ASUS Vivobook X1504VA / Intel Core i3-1315U.

## Evidence boundary

| Component | Identity | Current macOS status |
| --- | --- | --- |
| CPU | i3-1315U | Identity proven; full macOS path not proven |
| iGPU | PCI 8086:A7A9 | Acceleration not proven |
| VMD | PCI 8086:09AB / 8086:A77F | Storage path not proven |
| NVMe | KIOXIA KBG60ZNS512G | Depends on VMD resolution |
| Audio | Realtek 10EC:0256 / ALC256 family | AppleALC codec family proven; exact layout not proven |
| Wi-Fi | MediaTek 14C3:7902 | macOS support not proven |
| Bluetooth | USB 13D3:3579 | macOS support not proven |
| Touchpad | ASUS ASUF1300 / I2C HID | ACPI path not proven |

## Why the gate is conservative

WhateverGreen currently detects Alder Lake/Raptor Lake/Arrow Lake CPU generations, but its current Intel graphics implementation explicitly marks Rocket Lake, Alder Lake, Raptor Lake and Arrow Lake platform graphics as unsupported in the relevant graphics path. CPU-generation detection therefore must not be interpreted as proof of iGPU acceleration.

The project consequently refuses to emit a bootable-looking EFI candidate while the X1504VA GPU and VMD paths remain unresolved.

## External evidence

- WhateverGreen: https://github.com/acidanthera/WhateverGreen
- WhateverGreen Intel graphics implementation: https://github.com/acidanthera/WhateverGreen/blob/master/WhateverGreen/kern_igfx.cpp
- WhateverGreen changelog: https://github.com/acidanthera/WhateverGreen/blob/master/Changelog.md
- Dortania OpenCore Install Guide: https://dortania.github.io/OpenCore-Install-Guide/
- AppleALC supported codecs: https://github.com/acidanthera/AppleALC/wiki/Supported-codecs

Linux MT7902 drivers found in the investigation are not treated as macOS evidence.
