from __future__ import annotations

import argparse
import json
from pathlib import Path

from .acpi import find_nodes
from .manifest import write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(prog="hackintosh-platform")
    sub = parser.add_subparsers(dest="command", required=True)

    manifest = sub.add_parser("manifest")
    manifest.add_argument("profile")
    manifest.add_argument("output")
    manifest.add_argument("--source", action="append", default=[])

    acpi = sub.add_parser("acpi")
    acpi.add_argument("dsl")
    acpi.add_argument("--name", action="append", default=[])

    args = parser.parse_args()
    if args.command == "manifest":
        write_manifest(args.profile, args.output, args.source)
        return 0

    text = Path(args.dsl).read_text(encoding="utf-8", errors="replace").splitlines()
    names = set(args.name or ["GFX0", "VMD0", "NVD1", "ETPD"])
    print(json.dumps([node.to_dict() for node in find_nodes(text, names)], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
