from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Iterable

@dataclass
class GraphNode:
    name: str
    path: str
    adr: str | None = None
    parent: str | None = None
    children: list[str] = field(default_factory=list)
    def to_dict(self): return {"name":self.name,"path":self.path,"adr":self.adr,"parent":self.parent,"children":self.children}

def build_graph(lines: Iterable[str]) -> dict[str, GraphNode]:
    device_re=re.compile(r"^\s*Device\s*\(\s*([A-Za-z0-9_]+)\s*\)")
    scope_re=re.compile(r"^\s*Scope\s*\(\s*([^)]*)\s*\)")
    adr_re=re.compile(r"Name\s*\(\s*_ADR\s*,\s*([^)]*)\s*\)")
    nodes={}; stack=[]
    for line in lines:
        m=scope_re.match(line)
        if m: stack.append((m.group(1).strip(),1)); continue
        m=device_re.match(line)
        if m:
            name=m.group(1); parent=stack[-1][0] if stack else None; path=f"{parent}.{name}" if parent else name
            nodes[path]=GraphNode(name,path,parent=parent)
            if parent in nodes: nodes[parent].children.append(path)
            stack.append((path,1)); continue
        if stack:
            path,depth=stack[-1]
            if path in nodes:
                m=adr_re.search(line)
                if m and nodes[path].adr is None: nodes[path].adr=m.group(1).strip()
            depth += line.count("{")-line.count("}"); stack[-1]=(path,depth)
            while stack and stack[-1][1] <= 0: stack.pop()
    return nodes

def topology_for(lines: Iterable[str], names: set[str]) -> list[dict]:
    return [n.to_dict() for n in build_graph(lines).values() if n.name in names]
