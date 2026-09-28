from __future__ import annotations
import json, uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

@dataclass
class Experiment:
    id: str
    hypothesis: str
    candidate_sha: str | None = None
    status: str = "PLANNED"
    observations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def observe(self,text): self.observations.append(text)
    def close(self,status):
        if status not in {"PASSED","FAILED","ABORTED"}: raise ValueError("invalid experiment status")
        self.status=status

def new_experiment(hypothesis,candidate_sha=None): return Experiment(uuid.uuid4().hex,hypothesis,candidate_sha)
def save_experiment(experiment,path):
    with open(path,"w",encoding="utf-8") as f: json.dump(asdict(experiment),f,indent=2); f.write("\n")
