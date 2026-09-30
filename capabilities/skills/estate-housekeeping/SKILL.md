---
name: estate-housekeeping
description: "Keep Mike's Aside estate tidy: archive finished chats, file chats and routines into project folders, find dead or silent routines, close stale agent tabs, and keep the daily Kanban board honest. Use for 'clean up chats', 'organize chats into projects', 'archive everything except pinned', 'close unused tabs', or a chat audit."
---

# estate-housekeeping

1. **Inventory.** List chats and routines through the `aside` skill (`aside.sessions.list`, `aside.routines.list`). Pinned chats are never touched.
2. **Propose in a table.** Each row: chat or routine, proposed project folder or action (archive, file, pause), and the reason. Show it before changing anything large.
3. **Apply reversibly.** File with `aside.sessions.update` (project), archive with `aside.sessions.archive` (undo: `unarchive`). Pause or resume a routine only when Mike asked for that routine.
4. **Verify by re-listing,** not by the call's return value.

## Facts that cost time before
- Archiving a chat does not stop it if it is still running.
- `closeTab()` can report a close it did not perform; confirm with `listBrowserTabs()`.
- An active routine list does not mean anything ran; check each routine's sessions and their last status.
- The daily board is the Kanban at `http://127.0.0.1:8913` (`kanban.py` alongside it); new work is filed there, not in a second tracker.

## Done-test
The re-listed state matches the approved table row for row, and no pinned chat changed.
