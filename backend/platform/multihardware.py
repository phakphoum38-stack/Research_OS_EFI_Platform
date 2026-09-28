from __future__ import annotations
import json
from pathlib import Path

def discover_profiles(directory="hardware"):
    profiles=[]
    for path in sorted(Path(directory).glob("*.json")):
        try: data=json.loads(path.read_text(encoding="utf-8")); profiles.append({"path":str(path),"machine":data.get("machine"),"profile":data})
        except (OSError,json.JSONDecodeError): pass
    return profiles
