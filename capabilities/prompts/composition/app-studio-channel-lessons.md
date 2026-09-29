# App Studio channel lessons: from a channel's lessons.jsonl to the prompt library - draft v1

How a lesson mined from one of the ten build channels becomes App Studio prompt text, a firing
rule, a hierarchy row and an index row. Every step below is mechanical; the only judgment is
Step 1, and its tie-break goes to a person, not to a guess.

## Inputs (written by the channel workers; this procedure only reads them)

`capabilities/skills/youtube-<slug>/references/`:

- `lessons.jsonl`: one lesson per line. The merge needs `lesson_id`, `mandated_check` (one
  imperative sentence) and the video ids in its evidence.
- `stage-map.json`: the App Studio stage each lesson belongs to (one of the 11 stages).
- `bench-candidates.json`: candidate App Bench tasks. Not part of this merge: they go to whoever
  owns `bench/tasks/`.

A lesson missing any of those fields is recorded `BLOCKED: <lesson_id> <missing field>` and skipped.
Never fill a field by inference.

## Ids

A channel lesson is cited as `CH-<CODE>-NN` (two or three digits). Codes:

| code | channel | code | channel |
|---|---|---|---|
| JSM | JavaScript Mastery | SSG | Sonny Sangha |
| CWA | Code With Antonio | TRV | Traversy Media |
| LMA | Lama Dev | JTC | Josh tried coding |
| CDS | Codesistency | GXD | Galaxies.dev |
| NJD | notJust.dev | PYG | Piyush Garg |

The CH id is resolved only through its row in `capabilities/skills/app-studio/references/prompts.md`
(`## Channel lessons`), and that row names the source line as
`capabilities/skills/youtube-<slug>/references/lessons.jsonl#<lesson_id>`. `validate_hierarchy.py`
V9 fails a prompt that cites a CH id with no row, a row with no source, and a row whose source line
does not exist. Use the real folder name the worker wrote; V9 checks it.

## Step 1: classify each lesson (code first, then a person)

| class | test (deterministic) | result |
|---|---|---|
| DUPLICATE | its action is already an active LA or TG lesson for the same stage | no prompt change; the index row says `same as <LA/TG id>` in `carried by` |
| ADDITION | exactly one existing sub-prompt owns that stage and the same stack or artifact (its rule in `bench/prompt-rules.json` fires on the same field) | the next version of that sub-prompt carries the lesson |
| NEW FRAGMENT | no sub-prompt owns that stack, vendor or artifact | a new `app-sub-<slug>` whose parent is `app-studio-<stage>` from stage-map.json (a role prompt when the lesson is about building or verifying in general) |
| TIE | more than one candidate, or the stage is unclear | goes on the conductor's list with a recommendation; nothing is filed |

No JEV rubric is calibrated for lesson placement, so do not invent one: a tie is DEFERRED to a
person. JEV gates the resulting prompt text (Step 2a), not the placement.

Batch by prompt: every lesson that lands in the same prompt in one merge goes into one new version,
not one version per lesson.

## Step 2: the four edits, in this order

**(d) Index row first**, so V9 can resolve the id. Append to `references/prompts.md` under
`## Channel lessons`:

`| CH-JSM-07 | <the imperative, as it will appear in the prompt> | <video ids> | capabilities/skills/youtube-<slug>/references/lessons.jsonl#<lesson_id> | <prompt ids> |`

**(a) Prompt text.** Write the body in the family template: title, `Contract` block (id, version,
tier, parent, stage, audience, inputs, output, lessons carried, gates, done_when, stop with the
Gate-D clause), the numbered steps, the Evidence rule. A carried channel lesson is one header line:

`  - CH-JSM-07: <imperative> (<channel> videos: <ids>)`

and at least one numbered step that acts on it, citing `(CH-JSM-07)`. File it with
`~/Desktop/Projects/rig-app-studio/bench/prompt-file.py`:

```sh
# new fragment
bench/prompt-file.py new --id app-sub-<slug> --body body.md --task "App Studio sub-prompt: ..." \
  --tier sub --parent app-studio-<stage> --stage <stage> --audience builder \
  --lessons "CH-JSM-07 LA-24" --triggers "a distinctive phrase, another"
# addition to an existing prompt (next version; versions are immutable)
bench/prompt-file.py version --id app-sub-json-store --body body.md --lessons "LA-24 TG-20 CH-JSM-07"
```

The filer runs `rig-s1gate check app.prompt` and files only on PASS with contract_stated,
evidence_done, lessons_actionable and stop_rules above 0.9. A DEFERRED classifier files nothing
(exit 3). It keeps the family fields (tier, parent, stage, audience, lessons, jev) that
`tools/ingest.mjs` would drop, and it appends the hash-chained ledger line through `tools/lib.mjs`.

**(c) Hierarchy row.** For a new fragment:

1. Add `("app-sub-<slug>", "app-studio-<stage>", "<stage>", "builder")` to `PROMPTS["sub"]` in
   `capabilities/skills/app-studio/scripts/build_hierarchy.py`.
2. File the next version of the parent prompt with the new id on its `sub-prompts owned:` line.
   V9 requires every sub to be owned by exactly its parent.
3. Run `build_hierarchy.py`.

An addition needs no new row.

**(b) Firing rule.** For a new fragment, add to `bench/prompt-rules.json` under `subs`:

`"app-sub-<slug>": {"any": [{"field": "stack.<key>", "re": "(?i)<vendor|artifact>"}]}`

Match a specific stack key, never the joined `stack`: `stack.deviations` names the vendors a task
replaced, so a joined-stack match fires the wrong fragment. An addition keeps its existing rule.

## Step 3: gates (all must be green before the merge is reported)

```sh
cd ~/Developer/rig-capabilities
python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py        # 0 violations
for p in bad_path orphan_sub unwired_sub stage_gap kind_unregistered prompt_orphan engine_path_missing engine_commit_missing; do
  python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py --plant $p; test $? -eq 2 || echo "PLANT ESCAPED: $p"; done
node capabilities/prompts/tools/route.mjs --selftest && node capabilities/prompts/tools/route.mjs --write-routing
cd ~/Desktop/Projects/rig-app-studio && /usr/bin/python3 bench/prompt-selftest.py
```

`validate_hierarchy.py` also fails any prompt whose carried LA text no longer matches the ledger's
current `mandated_check`, so a ledger edit forces a new prompt version. It checks LA lines only:
compare each carried CH line with its source line by hand at merge time.
