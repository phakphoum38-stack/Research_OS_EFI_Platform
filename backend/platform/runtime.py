from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def fingerprint(path):
    d=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): d.update(chunk)
    return d.hexdigest()

def record_runtime_event(event,artifacts=None):
    return {"schema_version":"1.0","timestamp":datetime.now(timezone.utc).isoformat(),"event":event,
            "artifacts":[{"path":p,"sha256":fingerprint(p)} for p in (artifacts or []) if Path(p).is_file()]}

def write_runtime_event(event,output,artifacts=None):
    Path(output).write_text(json.dumps(record_runtime_event(event,artifacts),indent=2)+"\n",encoding="utf-8")
