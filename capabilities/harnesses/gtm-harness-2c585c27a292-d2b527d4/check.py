import json,sys
from creator_platform.intelligence import artifact_gate
result=artifact_gate(json.load(sys.stdin))
print(json.dumps(result))
sys.exit(0 if result["status"]=="PASS" else 1)
