class AuthorityBoundaryError(ValueError): pass
class AuthorityBoundary:
 def evaluate(self,packet,owner_authorized=False):
  if packet.get("owner_authority_required") is not True: raise AuthorityBoundaryError("owner_authority_required")
  pre=packet.get("pre_authority")=="PASS"
  return {"owner_authority_required":True,"owner_authorized":bool(owner_authorized),"pre_authority_pass":pre,"merge_authorized":bool(owner_authorized and pre),"hardware_mutation_authorized":False}
