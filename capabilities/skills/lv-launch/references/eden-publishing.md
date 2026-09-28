# Eden publishing: the only publisher

Eden is the single publisher of record for every lane. Postiz is retired by Mike's explicit instruction and is never routed to. Eden itself is a tool surface: `eden-mcp` drives the Canvas MCP server and `eden-linkedin-platform` drives the LinkedIn ops. Eden-side skills are cited by name, not by path.

## Preconditions before Eden is touched

1. The critique verdict is `ship`, with the score on the record.
2. The lane is named: A, B, client or job search. One post, one lane, one account.
3. Mike has approved this post in this session, having seen the final text. A blanket "approve everything" does not cover an outward public action.

## Check the connection first

The Eden MCP server can be enabled while unconnected: no `eden_*` tool exists in the session inventory in that state. Verify by inventory contents, never by the config write. If the tools are absent, report `blocked: eden-not-connected` and stop. There is no programmable connect method, and a browser workaround around a missing MCP connection is not acceptable.

## Tool routing

| Need | Tool |
|---|---|
| which workspace | `eden_list_workspaces` |
| does a slot already exist | `eden_list_schedules`, always first |
| what is queued or drafted | `eden_list_scheduled_posts` with a status filter; there is no `eden_list_posts` |
| staging the draft | `eden_draft_post`; its dedup path must carry the full post shape |
| his own analytics | `eden_list_analytics_posts`; a zero count right after publish is analytics lag, not failure |
| reusable Eden-side instructions | `eden_list_skills` / `eden_get_skill` / `eden_import_skill`, by name (for example `rig-linkedin-post-engine`) |

## Rules

- **Never auto-schedule.** Offer it. Eden's scheduler is not trusted for delivery; publishing stays by hand until a test post demonstrably lands. A live schedule or a publish needs Mike's explicit yes for that post.
- **Read the draft back out of Eden and diff it** against the approved text. A write call is not persistence evidence.
- **Structured results decide.** An `invalid` status means fix the input; do not retry the same payload. `conflict`, `forbidden` or `not-found` go to Mike.
- **Queue state is read over MCP, not the web UI.** The SPA renders stale and cancelled rows, and a blank-looking grid read through `innerText` is not an empty setting; read `input.value` before reporting a schedule as unset.
- **No scheduled-post delete API exists.** Cancellation happens in the Eden UI; alert and document the miss instead of assuming a delete landed.
- **Eden has zero comment or reply tools,** including no verification lane. Comments are posted and verified on LinkedIn itself; a receipt file with the exact comment text, timed a couple of minutes after publish, is the pattern that works. Never cite an "Eden-confirmed" receipt for a comment.
- Auto-DM rules are API-managed and are outward actions: the production landing page must be live before a rule fires publicly, and Mike approves the full-system run.

Absorbed from: lg-publish, eden-mcp, eden-linkedin-platform, step-5-publish.
