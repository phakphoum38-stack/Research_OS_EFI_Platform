import hashlib,json
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
def canonical_json(v): return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def digest(v): return hashlib.sha256(canonical_json(v)).hexdigest()
@dataclass(frozen=True)
class EvidenceEnvelope:
 schema_version:str; evidence_id:str; source_sha:str; kind:str; status:str; payload:dict; provenance:dict; created_at:str
 @classmethod
 def create(cls,source_sha,kind,status,payload,provenance):
  body={"source_sha":source_sha,"kind":kind,"status":status,"payload":dict(payload),"provenance":dict(provenance)}
  return cls("1.0",digest(body),source_sha,kind,status,dict(payload),dict(provenance),datetime.now(timezone.utc).isoformat())
 def to_dict(self): return asdict(self)
def verify_envelope(v):
 return v.get("evidence_id")==digest({k:v[k] for k in ("source_sha","kind","status","payload","provenance")})
