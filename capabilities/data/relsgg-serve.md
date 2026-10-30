# relsgg-serve — RelateAnything open-vocabulary relation extraction (RIG fleet vision tool)

Status: LIVE (2026-10-01). Primary host: rig48gb-ts (Apple M5 Max, 48GB) at
http://192.168.68.89:8888. Secondary: rig28gb (Apple M4 Pro) at http://192.168.68.60:8888.
Both run the same wrapper on port 8888 with LaunchAgent com.rig.relsgg-serve.

## What it is
Open-vocabulary scene-graph relation prediction (maelic/relsgg-vits16plus, DINOv3
ViT-S/16+, 53.2M params). Input: an image + object regions (boxes [x1,y1,x2,y2]
pixels). Output: scored (subject, relation, object) triplets, e.g.
`person ->riding [0.67]-> horse`. The relation vocabulary is supplied at inference
as any strings — no retraining.

## What it is NOT
It is a specialized vision TOOL, not a general VLM. It does not detect objects,
describe images, answer questions about images, or read UI mockups holistically.
A general image-analysis VLM is still a separate gap.

## Endpoints
- Service: http://192.168.68.89:8888 (rig48gb-ts LAN, primary) and
  http://192.168.68.60:8888 (rig28gb, secondary/fallback), stdlib ThreadingHTTPServer,
  model loaded once at startup, ~270-390 ms/predict on CPU.
  - `GET /health` -> {"status":"ok","model":"relsgg-vits16plus"}
  - `GET /info` -> load info + default predicate list
  - `POST /predict` -> {"image_b64"|"image_path", "boxes":[[x1,y1,x2,y2],...],
    "labels":[...], "vocabulary":[...], "topk":N, "box_scores":[...], "decompose":bool}
    -> {"triplets":[{subject,relation,object,score,subject_idx,object_idx,subject_box,object_box}],
        "spatial":[...], "semantic":[...]} (last two iff decompose=true)
- MCP bridge (stdio): `~/.rig/bin/mcp-relsgg` -> tools `relate_anything_health`,
  `relate_anything_predict`. Registered in `~/.omp/agent/mcp.json` (mcpServers.
  relate-anything) and Aside `~/.aside/u/0/settings.json` (mcp.servers.relate-anything).
  Override endpoint with RELSGG_BASE_URL.

## Install/run
- Node dir: `~/relsgg/` (venv on Python 3.12.12, `relsgg==1.0.0`, torch 2.14.1,
  weights cached in ~/.cache/huggingface).
- LaunchAgent `com.rig.relsgg-serve` (KeepAlive/RunAtLoad), log:
  `~/Library/Logs/relsgg-serve.log`, run script `~/relsgg/run.sh`.

## Verified
2026-10-01 from this Mac against rig48gb-ts: /health 200 ok; /predict on a
generated 800x600 two-box PNG returned ground-truth-correct spatial triplets
(blue block ->right of-> red block, red block ->left of-> blue block); a real
1280x799 JPEG over image_b64 decoded and returned coherent triplets.
