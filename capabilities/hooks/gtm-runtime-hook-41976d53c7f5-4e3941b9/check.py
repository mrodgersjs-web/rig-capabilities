import json,sys
from creator_platform.runtime import check
result=check(json.load(sys.stdin))
print(json.dumps(result))
sys.exit(0 if result["status"]=="PASS" else 1)
