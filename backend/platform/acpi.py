from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


_DEVICE_RE = re.compile(r"^\s*Device\s*\(\s*([A-Za-z0-9_]+)\s*\)")
_SCOPE_RE = re.compile(r"^\s*Scope\s*\(\s*([^)]*)\s*\)")
_ADR_RE = re.compile(r"Name\s*\(\s*_ADR\s*,\s*([^)]*)\)")


@dataclass
class AcpiNode:
    name: str
    path: str
    adr: str | None = None
    children: list["AcpiNode"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "path": self.path, "adr": self.adr, "children": [c.to_dict() for c in self.children]}


def extract_device_blocks(lines: Iterable[str]) -> list[AcpiNode]:
    """Extract a lightweight ACPI device map without compiling AML."""
    nodes: list[AcpiNode] = []
    scopes: list[str] = []
    pending: AcpiNode | None = None
    depth = 0
    for line in lines:
        scope = _SCOPE_RE.match(line)
        if scope:
            scopes.append(scope.group(1).strip())
        device = _DEVICE_RE.match(line)
        if device:
            name = device.group(1)
            prefix = scopes[-1] if scopes else ""
            path = f"{prefix}.{name}" if prefix else name
            pending = AcpiNode(name=name, path=path)
            nodes.append(pending)
            depth = 1
            continue
        if pending and depth:
            adr = _ADR_RE.search(line)
            if adr and pending.adr is None:
                pending.adr = adr.group(1).strip()
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                pending = None
        elif scopes and "}" in line:
            scopes.pop()
    return nodes


def find_nodes(lines: Iterable[str], names: set[str]) -> list[AcpiNode]:
    return [node for node in extract_device_blocks(lines) if node.name in names]
