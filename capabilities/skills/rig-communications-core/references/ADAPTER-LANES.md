# Adapter Lanes (v14) — multimodal hand-offs from text surfaces

Comms OS produces the TEXT/SCORE; studios render the media. Every hand-off is
recorded in the media ledger (`python3 -m rig_comms media ...`) with generator,
provenance and `path_exists` — a ledger row never claims a file that isn't there.

| from | to | lane | service | status today |
|---|---|---|---|---|
| linkedin/substack | hero image | `higgsfield-generate` (MCSLA) → media ledger | Higgsfield API | ADAPTER READY — needs live run + Gate-D |
| songs | audio | SUNO via `rig-communications-core/references` suno-architecture; shareable-feedback loop is the outcome metric | SUNO | SPEC ONLY — no API lane built |
| film-scripts | treatment→video | `rig-film-studio` 13-stage pipeline; scripts are the packet artifact | Higgsfield/C4D | SPEC ONLY |
| novels/film | narration | `media-use` TTS (HyperFrames audio engine) | local/HeyGen | SPEC ONLY |
| substack | repurpose set | `rig-repurpose-engine` | local | WIRING EXISTS upstream |

## Honest BLOCKED rule (v14.9)

An adapter that cannot run records `BLOCKED:<service-name>` in its lane log and
stops — it NEVER substitutes a mock, a placeholder file, or a silent skip.
Blocked today: Higgsfield (Gate-D on spend), SUNO (no lane), YouTube refresh
(IP block), Ollama embeds (service not listening). Each name is written where
the next operator will look, not buried.
