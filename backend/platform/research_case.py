from dataclasses import dataclass,asdict
@dataclass(frozen=True)
class ResearchCase:
 case_id:str; source_sha:str; profile:str; hypothesis:str; facts:tuple=(); observations:tuple=(); provenance:tuple=()
 def to_dict(self): return asdict(self)
 @classmethod
 def from_profile(cls,case_id,source_sha,profile_name,hypothesis,profile,provenance):
  return cls(case_id,source_sha,profile_name,hypothesis,tuple({"component":k,"value":v} for k,v in profile.items() if isinstance(v,dict)),(),tuple(provenance))
