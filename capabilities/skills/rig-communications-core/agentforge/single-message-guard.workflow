{
  "name": "single-message-guard",
  "description": "One outbound message, guarded: CommunicationGuard pass, E-score report, then Gate-D human approval. Blocked without approval; never auto-sends.",
  "steps": [
    {"name": "guard-pass", "action": "guard", "input": "draft", "channel": "email", "max_attempts": 2, "output": "verdict"},
    {"name": "score-draft", "action": "evaluate", "input": "draft", "channel": "email", "output": "score"},
    {"name": "gate-d-approval", "action": "human_approval", "input": "approved"}
  ]
}
