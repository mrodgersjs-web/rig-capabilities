# awesome-writing-tools — Integrated Catalog

Source: [Guido1Alessandro1Trevisan/awesome-writing-tools](https://github.com/Guido1Alessandro1Trevisan/awesome-writing-tools)
(a curated list of tools for improving written communication).

Every tool on the list is registered in `rig_comm/integrations/writing_tools.py`
(`TOOLS` / `catalog()`). The three open-source prose linters that run headlessly
without credentials ship **live wrappers** and are aggregated by `analyze()`.
Everything else (SaaS, API-key, desktop app, reference) is catalogued honestly
with `runnable=False` — there is no fake wrapper pretending to call Grammarly.

The subprocess linters are an **advisory** layer. The deterministic offline
`core.evaluate` ship gate is untouched.

**Link audit (2026-09-16, `curl -sL`):** all 23 source URLs return HTTP 200.
Notable drift, recorded per-entry in `TOOLS[*].audit`: **Atomic Reach** now
redirects to RAD Intel (`radintel.ai`) — original product defunct; **toprank**
repo renamed to `nowork-studio/notfair-plugin`; **Readable.io** → `readable.com`;
**JigSaw** → `jigsaw.google`. No dead links.

---

## Wired — live wrappers (run locally via a global binary or `npx`)

| Tool | Package | Catches | Wrapper |
|------|---------|---------|---------|
| [**Alex.js**](http://alexjs.com/) | `alex` | Insensitive / inconsiderate phrasing (gender, race, religion, ability) | `run_alex(text)` |
| [**Write Good**](https://github.com/btford/write-good) | `write-good` | Passive voice, weasel words, wordy phrases, cliches | `run_write_good(text)` |
| [**Markdownlint**](https://github.com/markdownlint/markdownlint) / [**markdownlint-cli**](https://github.com/igorshubovych/markdownlint-cli) | `markdownlint-cli` | Markdown style issues (headings, spacing, trailing whitespace) | `run_markdownlint(text)` |

```bash
# analyze a file with every available linter
rig writing-tools README.md

# analyze literal text, only one linter
rig writing-tools --text "The master whitelist is managed by a crazy salesman." --tool alex

# print the full catalog
rig writing-tools --list
```

```python
from rig_comm.integrations import writing_tools_analyze
results = writing_tools_analyze("So the report was written by John.")
for name, res in results.items():
    print(name, res.available, res.ran, res.to_dict()["count"])
```

Each wrapper returns a `ToolResult(available, ran, findings, error, raw)`.
`available=False` means neither the binary nor `npx` is on PATH; `ran=False`
with `available=True` means the tool could not bootstrap (offline / uncached).
Nothing raises.

---

## Catalogued — not runnable headless (SaaS / API key / desktop / reference)

| Tool | Kind | Why not wired |
|------|------|---------------|
| [Atomic Reach](https://www.atomicreach.com/) | SaaS (defunct) | Redirects to RAD Intel (radintel.ai); original product gone |
| [The Chicago Manual of Style](http://www.chicagomanualofstyle.org/home.html) | reference | Subscription style guide, human reference |
| [Chisel Editor](https://egonschiele.github.io/chisel-docs/) | desktop app | Interactive AI writing editor |
| [CiteMe](https://citeme.app/) | SaaS | Hosted citation generator + extensions |
| [Cliche Finder](http://cliche.theinfo.org/) | web app | Hosted-only, no package |
| [Contributor Covenant](https://www.contributor-covenant.org/) | reference | Code-of-conduct template |
| [Danger](https://github.com/danger/danger) | npm CLI | Needs a repo + CI PR context, not arbitrary text |
| [Grammarly](https://www.grammarly.com/) | SaaS | Paid, no headless API |
| [The Hemingway Editor](http://www.hemingwayapp.com/) | web/desktop | No CLI |
| [Inkwell](https://github.com/4worlds4w-svg/inkwell) | desktop app | Markdown editor (Rust/Tauri) |
| [JigSaw](https://jigsaw.google.com/projects/) | reference | Project hub, not a tool (now jigsaw.google) |
| [Kindling](https://kindlingwriter.com) | desktop app | Novel-writing app (Rust/Tauri) |
| [LanguageCheck](https://github.com/JohannesBuchner/languagecheck) | python CLI | LaTeX-paper specific; needs LaTeX source |
| [Perspective API](https://www.perspectiveapi.com/) | web API | Requires a Google API key |
| [ProWritingAid](https://prowritingaid.com/) | SaaS | Paid, no headless API |
| [Readable.io](https://readable.io/) | SaaS | Paid readability service (now readable.com) |
| [Taskade](https://taskade.com/) | SaaS | Collaborative outliner, not a check |
| [toprank](https://github.com/nowork-studio/toprank) | Claude plugin | Needs Search Console + CMS creds; repo renamed to notfair-plugin |
| [Weallbehave](https://github.com/wealljs/weallbehave) | npm CLI | Generates CODE_OF_CONDUCT.md; scaffolder, not a prose check |

To make a catalogued SaaS/API tool runnable later: add credentials + a wrapper
in `writing_tools.py`, flip its `runnable`/`wired` flags, and register a runner
in `_RUNNERS`.
