# Client store normalization

Purpose: turn entities into a flat, id-keyed client store with one fetching point, slice-level mutations, and derived indexes that never carry payload.

When to load: when shaping the store, placing fetching points, wiring mutations, or deciding how components read data.

## Step checklist

1. Name one map per entity, keyed by id, and one map per view (dashboard by tag, search results, per-contact messages).
2. Place exactly one fetching point at the page or content level; pass ids or small lists down, never whole nested payloads.
3. Let children read their own record from the store by id at render time.
4. Define mutations as slice updates: create, update and delete touch one record (plus its index entries), never the whole tree.
5. Build derived structures (interval trees, dependency graphs, search tries) id-only, and update them separately from the payload maps.
6. Route every state change through one dispatcher plus handler, and let DOM-level observation feed that path rather than mutate state directly.
7. Set sync markers (last-sync timestamp) as state so incremental pulls are cheap.
8. State write ownership out loud: one writer, all other windows or components read-only.

## Laws

- Store client data normalized and flattened as id-keyed maps; nested multi-level structures are
  costly to access. Consensus.
  (CLAIM(3MADCVqL534@32:14, 5vyKhm2NTfw@19:33, leo1FZ6vu1I@13:10, tsGarhpWOws@34:56))
- Fetch at the page level and pass ids down; each child reads its own record from the store by id.
  Consensus. (CLAIM(3MADCVqL534@33:16, 5vyKhm2NTfw@20:55, Tu-hZ6lqNtY@24:46))
- Keep a view store (tag id to item list) and a search store alongside the entity stores.
  Single-source. (CLAIM(Tu-hZ6lqNtY@26:44))
- Normalize per-contact data: contacts by id, message arrays per contact id, attachments as an
  optional collection. Single-source. (CLAIM(LEaiGjffLEs@25:56))
- Sync from a timestamp checkpoint: send the last-sync marker so the client only pulls records newer
  than that point. Single-source. (CLAIM(LEaiGjffLEs@26:30))
- Create, update and delete mutate only the changed slice of the store and never rebuild derived
  structures wholesale. Single-source. (CLAIM(leo1FZ6vu1I@10:29))
- Keep the server representation close to the client model so transformation code disappears.
  Single-source. (CLAIM(leo1FZ6vu1I@11:32))
- Keep the runtime state flat and asset-keyed (or entity-keyed) so any record is reachable in one
  lookup. Single-source. (CLAIM(HR2jXy_wPg4@27:59))
- Keep derived indexes id-only and mutate the id-keyed map separately, so payload edits never touch
  the search structure. Single-source. (CLAIM(leo1FZ6vu1I@31:44))
- Detect overlapping records with an interval tree keyed by start date and augmented with subtree
  maximum end, instead of scanning the list per unit. Single-source.
  (CLAIM(leo1FZ6vu1I@18:07))
- Wire the app through event-driven architecture: event bus, handler, async action, store,
  components. Single-source. (CLAIM(leo1FZ6vu1I@43:44))
- Split content into an editable region and a static region so the static part caches and re-render
  stays scoped. Single-source. (CLAIM(tsGarhpWOws@12:43))
- Track editable-DOM changes with MutationObserver and dispatch a single update-content action into
  the global store. Single-source. (CLAIM(tsGarhpWOws@13:06))
- Update state only through a global dispatcher plus action handler (reducer style), never by
  mutating from components. Single-source. (CLAIM(tsGarhpWOws@13:58))
- Give the parser or renderer access to the global store so it can wire data into components as an
  invisible controller. Single-source. (CLAIM(tsGarhpWOws@26:40))
- Keep app state minimal: root id plus normalized records, and a per-record hash to decide whether a
  cached static region must be re-rendered. Single-source. (CLAIM(tsGarhpWOws@34:42))
- Let extension windows read shared storage but never write it; route every write and fetch through
  the host window. Single-source. (CLAIM(HR2jXy_wPg4@60:03))

## Decision table

| Decision | Pick | When to deviate | Cites |
|---|---|---|---|
| Store shape | flat id-keyed maps | never nested trees for records read in more than one place | CLAIM(3MADCVqL534@32:14) |
| Fetching point | one per page/content level | add a second fetcher only for genuinely independent widgets | CLAIM(3MADCVqL534@33:16, Tu-hZ6lqNtY@24:46) |
| Payload passed to children | ids (or short list heads) | pass full records only when the child renders immediately and never re-reads | CLAIM(5vyKhm2NTfw@20:55) |
| Mutation granularity | slice update | full rebuild only when the server replaces the whole dataset | CLAIM(leo1FZ6vu1I@10:29) |
| Derived index contents | ids only | never payload; data belongs in the map | CLAIM(leo1FZ6vu1I@31:44) |
| Conflict or overlap detection | interval tree | linear scan is fine for tiny fixed lists only | CLAIM(leo1FZ6vu1I@18:07) |
| Update path | dispatcher + handler | direct mutation from components is not an option | CLAIM(tsGarhpWOws@13:58) |
| DOM-driven edits | MutationObserver into one action | per-node handlers leak and duplicate logic | CLAIM(tsGarhpWOws@13:06) |
| Incremental sync | timestamp checkpoint | full refetch when the dataset is small or history is rewritten | CLAIM(LEaiGjffLEs@26:30) |
| Multi-window state | single writer host | extensions read-only; never multi-writer | CLAIM(HR2jXy_wPg4@60:03) |

## Anti-patterns

- Writing response JSON straight into component state as nested objects (CLAIM(3MADCVqL534@32:14)).
- Fetching the same entity from several children and reconciling duplicates by hand
  (CLAIM(5vyKhm2NTfw@20:55)).
- Rebuilding an index or a derived list on every keystroke-level mutation (CLAIM(leo1FZ6vu1I@10:29)).
- Storing payload inside a derived index so one edit touches two structures (CLAIM(leo1FZ6vu1I@31:44)).
- Letting each window write shared storage and racing the others (CLAIM(HR2jXy_wPg4@60:03)).
- Pulling full history on every sync instead of from a checkpoint (CLAIM(LEaiGjffLEs@26:30)).

## Worked cases

- 3MADCVqL534, [Front-End System Design] - Pinterest: page-level fetch, ids down, id-keyed maps (CLAIM(3MADCVqL534@32:14, 3MADCVqL534@33:16)).
- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: one store map per entity type, components look up by feed id (CLAIM(5vyKhm2NTfw@19:33)).
- leo1FZ6vu1I, [Front-End System Design] - Google Calendar: slice mutations, id-only interval tree, event-bus wiring (CLAIM(leo1FZ6vu1I@31:44, leo1FZ6vu1I@43:44)).
- tsGarhpWOws, Frontend System Design - Notion-like editor: normalized page map, reducer-style dispatch, static-region hashing (CLAIM(tsGarhpWOws@13:58, tsGarhpWOws@34:42)).
- Tu-hZ6lqNtY, [Front-End Product Design] - Netflix: entity stores plus dashboard and search view stores (CLAIM(Tu-hZ6lqNtY@26:44)).
- LEaiGjffLEs, [Front-End System Design] - Chat application: per-contact arrays and checkpoint sync (CLAIM(LEaiGjffLEs@25:56, LEaiGjffLEs@26:30)).
- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: flat asset-keyed runtime state with a single writing window (CLAIM(HR2jXy_wPg4@27:59, HR2jXy_wPg4@60:03)).
