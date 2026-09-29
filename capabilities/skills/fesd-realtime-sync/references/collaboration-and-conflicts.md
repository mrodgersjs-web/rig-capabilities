# collaboration-and-conflicts (fesd-realtime-sync)

Purpose: state what this author actually covers about multi-writer data (live multi-user sync, conflict spotting, single-writer windows) and where he deliberately stops, so the design names its conflict stance instead of silently assuming one.

When to load: when two or more users or windows can write the same data (Sheets-like, Notion-like, Calendar-like products), when a design mentions "live collaboration", and when the conflict-resolution question comes up in review or an interview.

## Step checklist
1. List who can write the same entity (users, devices, windows) and whether writes arrive concurrently.
2. Separate the two problems he separates: conflict detection (a front-end concern he designs) versus conflict resolution (a distributed-systems problem he declares out of scope).
3. Write the detection model if overlapping or conflicting states must be visible to the user.
4. Write the sync path: initial chunk, incremental updates, and how updates enter client state.
5. For multi-window or multi-device, adopt the single-writer rule: one owner writes, the rest replicate.
6. State the resolution stance explicitly: last-write-wins, locking, OT, CRDT, or out of scope with a named owner. An unstated stance is a defect in this record.

## Laws (this stage)
- Let a correctly configured GraphQL layer keep client and server state in sync so subscription updates flow into client state automatically. single-source. CLAIM(tsGarhpWOws@43:03)
- Expose the live channel as a subscription interface so the transport underneath stays swappable while collaboration traffic grows. single-source. CLAIM(leo1FZ6vu1I@38:41)

## Laws (adjacent stages, cited because this sub-topic needs them)
Scope and detection
- Declare conflict resolution out of scope for a frontend system design, mention it, and move on rather than designing CRDTs. (stage S01) CLAIM(tsGarhpWOws@04:20)
- Enumerate multi-user behavior and conflict spotting as product requirements before constraints. (stage S02) CLAIM(leo1FZ6vu1I@01:50)
- Treat live updates from other users as a requirement, not a feature: others can create events for you and updates arrive live. (stage S02) CLAIM(leo1FZ6vu1I@02:11)
- Detect overlapping events with an interval tree (keyed by start date, augmented with subtree max end) instead of scanning the list per day. (stage S05) CLAIM(leo1FZ6vu1I@18:07)
- Keep the conflict index id-only and mutate the id-keyed map separately, so payload edits never touch the search structure. (stage S05) CLAIM(leo1FZ6vu1I@31:44)

Write ownership
- Designate one host window that owns all state writes and data fetching, with other windows acting as extensions. (stage S03) CLAIM(HR2jXy_wPg4@57:01)
- Let extension windows read shared storage but never write it; route every write and fetch through the host window. (stage S05) CLAIM(HR2jXy_wPg4@60:03)
- Use BroadcastChannel to pass structured events between windows instead of inventing a custom channel. (stage S03) CLAIM(HR2jXy_wPg4@58:58)

Sync mechanics
- Sync from a timestamp checkpoint: send the last-sync marker so the client only pulls data from that point onward. (stage S05) CLAIM(LEaiGjffLEs@26:30)
- Send content diffs to the server instead of whole pages, using a delta library to compute them. (stage S06) CLAIM(tsGarhpWOws@41:31)
- Keep entities JSON-serializable in both directions so export and import come for free. (stage S02) CLAIM(leo1FZ6vu1I@10:15)

## What he covers versus what he does not
| conflict mechanism | what the corpus gives | status |
|---|---|---|
| detection (spot the conflict) | interval tree over time ranges, surfaced to the user | designed, CLAIM(leo1FZ6vu1I@18:07) |
| last-write-wins | not discussed by name | gap; distiller note below |
| locking / edit leases | not discussed; the single-writer host/extension rule is the closest pattern | partial, CLAIM(HR2jXy_wPg4@57:01, HR2jXy_wPg4@60:03) |
| operational transform | not discussed | gap |
| CRDT | named only to be excluded from front-end scope | excluded, CLAIM(tsGarhpWOws@04:20) |
| resolution on concurrent edits | parked; the Sheets design covers no network at all and the Calendar multi-user story never follows through | gap, CLAIM(fmIiDLbLc_s@05:01) |

Distiller note (not the author): the honest stance for a front-end design is exactly what he does: name resolution as out of scope, own detection and sync, and record which system owns resolution (server or CRDT service). For product work, last-write-wins is the cheap default that loses edits silently; a per-entity version or timestamp check plus a visible "this changed elsewhere" state is the smallest step up. Modern editors (Yjs-style CRDT libraries) make CRDT a buy decision rather than a research project, which is why his 2023 "do not design CRDTs" is interview advice, not product advice.

Distiller note (not the author): his Sheets episode assumes no network layer at all, so nothing in this corpus demonstrates concurrent spreadsheet editing; if the product is Sheets-like, this sub-skill cannot carry the design and the collaboration model must come from elsewhere.

## Decision table
| situation | stance to write in the record | cite |
|---|---|---|
| read-heavy shared data (calendar view, feed) | server is source of truth; client subscribes and reconciles | CLAIM(tsGarhpWOws@43:03, leo1FZ6vu1I@36:54) |
| two views of one app (multi-window) | single writer, extensions replicate read-only | CLAIM(HR2jXy_wPg4@57:01, HR2jXy_wPg4@60:03) |
| overlapping records must be visible | detect client-side with an interval structure, index stays id-only | CLAIM(leo1FZ6vu1I@18:07, leo1FZ6vu1I@31:44) |
| concurrent text editing by two users | out of scope in this stage; name the owning system | CLAIM(tsGarhpWOws@04:20) |
| reconnect after a gap | timestamp checkpoint, pull deltas | CLAIM(LEaiGjffLEs@26:30) |

## Worked cases
- tsGarhpWOws: Frontend System Design - Notion-like editor. Conflict resolution explicitly parked; subscription keeps state in sync.
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. Multi-user as requirement, conflict spotting solved with an interval tree.
- HR2jXy_wPg4: Frontend System Design - Financial Dashboard / TradingView. Single-writer multi-window replication.
- fmIiDLbLc_s: [Front-End System Design] - Google Sheets. The collaboration gap by omission: offline single-user design, no sync section.
