import { randomUUID } from 'node:crypto';
import { EventEmitter } from 'node:events';
import { execFile } from 'node:child_process';
import { mkdirSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { chatComplete, } from './model-route.js';
import { estimateTokens, seatLadder } from './council-models.js';
import { buildEvidencePack, callBridge, checkCitations, } from './mcp-bridge.js';
import { gateVerdict, deliveryPack, strikeSeatNumbers, checkClaims, structuredVerdict, } from './verdict-gate.js';
import { classify as classifySeatTool, describe as describeSeatPolicy, seatForRole, } from './seat-policy.js';
const PRIME_ROLES = {
    zeus: 'chair',
    nemesis: 'critic',
    themis: 'judge',
};
export function defaultRole(name) {
    return PRIME_ROLES[name.trim().toLowerCase()] ?? 'worker';
}
export class RoomStore {
    db;
    ownerId;
    /** Emits 'change' with a roomId after every write; drives live streaming. */
    events = new EventEmitter();
    constructor(db, ownerId) {
        this.db = db;
        this.ownerId = ownerId;
        this.events.setMaxListeners(200);
        db.exec(`CREATE TABLE IF NOT EXISTS rooms(id TEXT PRIMARY KEY, ownerId TEXT NOT NULL, title TEXT NOT NULL, spaceId TEXT, createdAt INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS room_members(roomId TEXT NOT NULL, dotId TEXT NOT NULL, role TEXT NOT NULL, position INTEGER NOT NULL, PRIMARY KEY(roomId, dotId));
      CREATE TABLE IF NOT EXISTS room_turns(id TEXT PRIMARY KEY, roomId TEXT NOT NULL, runId TEXT, seq INTEGER NOT NULL, dotId TEXT, speaker TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, model TEXT, createdAt INTEGER NOT NULL, saw TEXT NOT NULL DEFAULT '[]');
      CREATE INDEX IF NOT EXISTS room_turns_room ON room_turns(roomId, seq);
      CREATE TABLE IF NOT EXISTS room_runs(id TEXT PRIMARY KEY, roomId TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, verdict TEXT, move TEXT, worker TEXT, decisionPath TEXT, taskPath TEXT, jevVerdict TEXT, jevDecisionId TEXT, error TEXT, startedAt INTEGER NOT NULL, endedAt INTEGER);`);
        if (!db
            .prepare('PRAGMA table_info(rooms)')
            .all()
            .some((column) => column.name === 'slug'))
            db.exec('ALTER TABLE rooms ADD COLUMN slug TEXT');
        if (!db
            .prepare('PRAGMA table_info(room_runs)')
            .all()
            .some((column) => column.name === 'jevEnforced'))
            db.exec('ALTER TABLE room_runs ADD COLUMN jevEnforced INTEGER');
        for (const [table, column, type] of [
            ['room_turns', 'phase', 'TEXT'],
            ['room_turns', 'meta', 'TEXT'],
            ['room_runs', 'protocol', 'TEXT'],
            ['room_runs', 'tier', 'TEXT'],
            ['room_runs', 'tokensIn', 'INTEGER'],
            ['room_runs', 'tokensOut', 'INTEGER'],
            ['room_runs', 'triage', 'TEXT'],
        ])
            if (!db
                .prepare(`PRAGMA table_info(${table})`)
                .all()
                .some((field) => field.name === column))
                db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${type}`);
        // A crash mid-debate must not leave a room locked forever.
        db.prepare("UPDATE room_runs SET status='failed', error='Server restarted during this debate.', endedAt=? WHERE status='running'").run(Date.now());
    }
    rooms() {
        return this.db
            .prepare('SELECT * FROM rooms WHERE ownerId=? ORDER BY createdAt DESC')
            .all(this.ownerId);
    }
    room(id) {
        const room = this.db
            .prepare('SELECT * FROM rooms WHERE id=? AND ownerId=?')
            .get(id, this.ownerId);
        if (!room)
            throw new Error('Room not found.');
        return room;
    }
    bySlug(slug) {
        return this.db
            .prepare('SELECT * FROM rooms WHERE slug=? AND ownerId=?')
            .get(slug, this.ownerId);
    }
    setSlug(roomId, slug) {
        this.db.prepare('UPDATE rooms SET slug=? WHERE id=?').run(slug, roomId);
        this.changed(roomId);
    }
    changed(roomId) {
        this.events.emit('change', roomId);
    }
    create(title, spaceId, members, slug = null) {
        const room = {
            id: randomUUID(),
            ownerId: this.ownerId,
            title,
            spaceId,
            createdAt: Date.now(),
            slug,
        };
        this.db.exec('BEGIN');
        try {
            this.db
                .prepare('INSERT INTO rooms (id, ownerId, title, spaceId, createdAt, slug) VALUES (?, ?, ?, ?, ?, ?)')
                .run(room.id, room.ownerId, title, spaceId, room.createdAt, slug);
            for (const member of members)
                this.db
                    .prepare('INSERT INTO room_members VALUES (?, ?, ?, ?)')
                    .run(room.id, member.dotId, member.role, member.position);
            this.db.exec('COMMIT');
        }
        catch (error) {
            this.db.exec('ROLLBACK');
            throw error;
        }
        return room;
    }
    members(roomId) {
        return this.db
            .prepare('SELECT * FROM room_members WHERE roomId=? ORDER BY position')
            .all(roomId);
    }
    addMember(roomId, dotId, role) {
        this.room(roomId);
        const next = Number(this.db
            .prepare('SELECT COALESCE(MAX(position), -1) AS p FROM room_members WHERE roomId=?')
            .get(roomId).p) + 1;
        this.db
            .prepare('INSERT INTO room_members VALUES (?, ?, ?, ?) ON CONFLICT(roomId, dotId) DO UPDATE SET role=excluded.role')
            .run(roomId, dotId, role, next);
        this.changed(roomId);
    }
    /** Leaves the room only; the Dot itself is never touched. */
    removeMember(roomId, dotId) {
        this.room(roomId);
        if (this.activeRun(roomId))
            throw new Error('Room is debating. Change members after the verdict.');
        if (this.members(roomId).length <= 2)
            throw new Error('Room needs at least two Dots to debate.');
        this.db
            .prepare('DELETE FROM room_members WHERE roomId=? AND dotId=?')
            .run(roomId, dotId);
        this.changed(roomId);
    }
    setRole(roomId, dotId, role) {
        this.room(roomId);
        if (this.activeRun(roomId))
            throw new Error('Room is debating. Change roles after the verdict.');
        const changes = this.db
            .prepare('UPDATE room_members SET role=? WHERE roomId=? AND dotId=?')
            .run(role, roomId, dotId).changes;
        if (!changes)
            throw new Error('Room member not found.');
        this.changed(roomId);
    }
    /** Moves a member one place earlier (-1) or later (+1) in speaking order. */
    move(roomId, dotId, delta) {
        const list = this.members(roomId);
        const index = list.findIndex((member) => member.dotId === dotId);
        const other = list[index + delta];
        if (index < 0 || !other)
            return;
        const update = this.db.prepare('UPDATE room_members SET position=? WHERE roomId=? AND dotId=?');
        update.run(other.position, roomId, dotId);
        update.run(list[index].position, roomId, other.dotId);
        this.changed(roomId);
    }
    turns(roomId) {
        return this.db
            .prepare('SELECT * FROM room_turns WHERE roomId=? ORDER BY seq')
            .all(roomId)
            .map((row) => ({
            ...row,
            saw: JSON.parse(String(row.saw ?? '[]')),
            meta: row.meta ? JSON.parse(String(row.meta)) : null,
        }));
    }
    addTurn(turn) {
        const seq = Number(this.db
            .prepare('SELECT COALESCE(MAX(seq), 0) AS s FROM room_turns WHERE roomId=?')
            .get(turn.roomId).s) + 1;
        const value = {
            ...turn,
            id: randomUUID(),
            seq,
            createdAt: Date.now(),
        };
        this.db
            .prepare('INSERT INTO room_turns (id, roomId, runId, seq, dotId, speaker, role, content, model, createdAt, saw, phase, meta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
            .run(value.id, value.roomId, value.runId, value.seq, value.dotId, value.speaker, value.role, value.content, value.model, value.createdAt, JSON.stringify(value.saw), value.phase ?? null, value.meta ? JSON.stringify(value.meta) : null);
        this.changed(value.roomId);
        return value;
    }
    runs(roomId) {
        return this.db
            .prepare('SELECT * FROM room_runs WHERE roomId=? ORDER BY startedAt')
            .all(roomId);
    }
    activeRun(roomId) {
        // 'awaiting-verdict' counts as open: a run with no structured verdict is
        // not done (fix 1, Mike 2026-10-06), and the room must not start another
        // debate on top of it.
        return this.runs(roomId).find((run) => run.status === 'running' || run.status === 'awaiting-verdict');
    }
    startRun(roomId) {
        const run = {
            id: randomUUID(),
            roomId,
            status: 'running',
            stage: 'starting',
            verdict: null,
            move: null,
            worker: null,
            decisionPath: null,
            taskPath: null,
            jevVerdict: null,
            jevDecisionId: null,
            error: null,
            startedAt: Date.now(),
            endedAt: null,
        };
        this.db
            .prepare("INSERT INTO room_runs (id, roomId, status, stage, startedAt) VALUES (?, ?, 'running', 'starting', ?)")
            .run(run.id, roomId, run.startedAt);
        this.changed(roomId);
        return run;
    }
    updateRun(id, patch) {
        const keys = Object.keys(patch);
        if (!keys.length)
            return;
        const row = this.db
            .prepare('SELECT roomId FROM room_runs WHERE id=?')
            .get(id);
        this.db
            .prepare(`UPDATE room_runs SET ${keys.map((key) => `${key}=?`).join(', ')} WHERE id=?`)
            .run(...keys.map((key) => patch[key]), id);
        if (row?.roomId)
            this.changed(row.roomId);
        if (patch.status === 'done' || patch.status === 'awaiting-verdict') {
            this.writeDeliveryFile(id);
        }
    }
    /** The run's delivery: the transcript plus the manifest a delivery gate
     *  grades — an artifact named, verified figures kept with their evidence
     *  ids, inferred claims kept apart, blockers plain. Never throws. */
    writeDeliveryFile(runId) {
        try {
            const run = this.db
                .prepare('SELECT * FROM room_runs WHERE id=?')
                .get(runId);
            if (!run)
                return;
            const turns = this.db
                .prepare('SELECT * FROM room_turns WHERE runId=? ORDER BY seq')
                .all(runId).map((turn) => ({
                ...turn,
                saw: JSON.parse(String(turn.saw ?? '[]')),
                meta: turn.meta ? JSON.parse(String(turn.meta)) : null,
            }));
            let confidence = '';
            let dissent = '';
            let packText = '';
            for (const turn of turns) {
                const meta = (turn.meta ?? {});
                if (meta.confidence)
                    confidence = meta.confidence;
                if (meta.dissent)
                    dissent = meta.dissent;
                if ((turn.role === 'judge' || turn.phase === 'verdict' || /\bVERDICT\s*:/i.test(turn.content || '')) && (!confidence || !dissent)) {
                    const sv = structuredVerdict(turn.content || '');
                    if (sv.confidence && !confidence) confidence = sv.confidence;
                    if (sv.dissent && !dissent) dissent = sv.dissent;
                }
                if (meta.evidencePack?.text)
                    packText = meta.evidencePack.text;
                // The pack's authoritative text is the room's own Tool bridge turn.
                if (turn.speaker === 'Tool bridge' && !packText)
                    packText = turn.content;
            }
            // Claim accuracy (relay xdjQtAGJmfSsidtm + hub SP4ikIin7S6GmLBw 2026-10-06):
            // every ranking, count or percentage claim in the seat turns and the
            // verdict is re-derived by code from the pack text its line cites.
            const claims = checkClaims(turns
                .filter((turn) => (turn.role !== 'system' && turn.role !== 'human') ||
                turn.phase === 'verdict')
                .map((turn) => `${turn.speaker}\n${turn.content}`)
                .join('\n'), packText);
            const runsDir = join(resolve(dirname(process.env.DATABASE_PATH ?? 'data/opendots.sqlite')), 'runs');
            mkdirSync(runsDir, { recursive: true });
            const transcriptPath = join(runsDir, `${runId}.md`);
            const rawTurnsPath = join(runsDir, `${runId}.transcript.md`);
            const transcript = turns
                .map((turn) => `## ${turn.seq} ${turn.role} ${turn.speaker}\n\n${turn.content}`)
                .join('\n\n---\n\n');
            const firstLine = String(turns[0]?.content ?? run.stage ?? '')
                .split('\n')[0]
                .slice(0, 120);
            const pack = deliveryPack({
                runId,
                topic: firstLine,
                transcriptPath: rawTurnsPath,
                verdict: String(run.verdict ?? ''),
                move: String(run.move ?? ''),
                confidence,
                dissent,
                turns: turns.map((turn) => ({
                    role: turn.role,
                    name: turn.speaker,
                    content: turn.content,
                })),
                pack: packText,
                claims,
            });
            // Pack first: the claims ledger is the deliverable, the transcript is
            // the reference record (lane.delivery grades the output as written).
            writeFileSync(transcriptPath, `${pack}\n`);
            writeFileSync(rawTurnsPath, `# Raw turn transcript (reference record, not the deliverable)\n\n${transcript}\n`);
            this.addTurn({
                roomId: String(run.roomId),
                runId,
                dotId: null,
                speaker: 'delivery',
                role: 'system',
                content: pack,
                model: null,
                saw: [],
                phase: 'delivery',
            });
        }
        catch (error) {
            // A delivery write must never break the run itself.
            console.error('opendots delivery write failed:', error);
        }
    }
}
// ---------------------------------------------------------------------------
// The debate engine.
const DOCTRINE = [
    'Room rules (they override any other instruction you carry):',
    '- The council must SOLVE, not veto. Every turn names or improves a concrete internal move.',
    '- Reply to the earlier speakers by name. Do not repeat what they said; build on it or attack it.',
    '- Nothing said in this room is permission to send, post, spend, or submit anything, and nothing here may involve a minor.',
    '- No invented numbers, employers, machines, reboots, or secrets.',
    '- Any number you write (count, percent, date, size) must carry an evidence id from the EVIDENCE block in the same turn, e.g. 6,380 (rcpt_0123abcd45). A number with no evidence id in its turn is treated as invented: it is struck and cannot appear in the verdict.',
    '- When a claim rests on the evidence, carry the figure beside the id: (rcpt_0123abcd45): 16 mentions, rank 9. A citation without its figure is a claim without backing - quote the figure the evidence actually shows, and never restate a rank, count, or percent from memory.',
    '- Claims must match their citation exactly. Every ranking, count or percentage claim is re-derived by code from the pack text the line cites: a figure that is not there, a quoted label that is not there, or a rank the evidence does not give (calling something top-ranked when its own receipt ranks it lower) rejects the run. Unknown facts go in [bracket] or [UNVERIFIED ...] and are labeled INFERRED, never VERIFIED.',
    '- This room is advisory by design: you have NO tools here (no browser, files, or shell). Before the debate the room may hand you an EVIDENCE block fetched by its read-only tool bridge; every item carries a receipt id like [rcpt_0123abcd45]. You may say something was checked, read, or verified ONLY by citing its receipt id inline, e.g. (rcpt_0123abcd45). Anything without a receipt was checked by nobody: say so, and never claim you ran, opened, checked, or changed anything yourself. An approved move is handed to Aside/OMP as a task file; they execute it under their own gates.',
    '- Answer in plain text only.',
].join('\n');
export const COUNCIL_SLUG = 'council';
export function parseVerdict(text) {
    const first = text
        .split('\n')
        .map((line) => line.trim())
        .find(Boolean) ?? '';
    const match = first
        .replace(/^\**\s*(Themis\s*:\s*)?/i, '')
        .replace(/^\**\s*VERDICT\s*\**\s*:\s*/i, '')
        .match(/^\**\s*(APPROVE|REJECT)\b\**\s*[:.\-–]?\s*(.*)$/i);
    if (!match)
        return { verdict: null, move: null };
    const verdict = match[1].toUpperCase();
    let move = match[2].trim();
    const named = text.match(/MOVE\s*:\s*(.+)/i);
    if (verdict === 'REJECT')
        move = named ? named[1].trim() : '';
    move = move.replace(/^\**|\**$/g, '').trim();
    return { verdict, move: move.length >= 8 ? move : null };
}
function stamp(now = new Date()) {
    return now
        .toISOString()
        .replace(/[-:]/g, '')
        .replace(/\.\d+Z$/, 'Z');
}
function defaultJudge(bin) {
    return (path, subject) => new Promise((resolve) => {
        execFile(bin, [
            'check',
            'council.judgment',
            '--file',
            path,
            '--subject',
            subject,
            '--json',
        ], { timeout: 90_000 }, 
        // Exit 1/2 are verdicts (BLOCK/ESCALATE), not failures: read stdout.
        (_error, stdout, stderr) => {
            try {
                resolve(JSON.parse(stdout || '{}'));
            }
            catch {
                resolve({
                    verdict: 'UNAVAILABLE',
                    decision_id: undefined,
                    enforced: undefined,
                    ...(stderr ? {} : {}),
                });
            }
        });
    });
}
export class RoomEngine {
    store;
    options;
    controllers = new Map();
    constructor(store, options) {
        this.store = store;
        this.options = options;
    }
    dot(id) {
        return this.options.dots().find((dot) => dot.id === id);
    }
    createRoom(title, dotIds, spaceId) {
        const unique = [...new Set(dotIds)];
        if (unique.length < 2)
            throw new Error('Room needs at least two Dots to debate.');
        const members = unique.map((dotId, position) => {
            const dot = this.dot(dotId);
            if (!dot)
                throw new Error('Dot not found.');
            return {
                roomId: '',
                dotId,
                role: defaultRole(dot.name),
                position,
            };
        });
        return this.store.create(title, spaceId ?? this.dot(unique[0])?.spaceId ?? null, members);
    }
    view(roomId) {
        const room = this.store.room(roomId);
        const members = this.store.members(roomId).map((member) => {
            const dot = this.dot(member.dotId);
            return { ...member, name: dot?.name ?? 'Unknown Dot' };
        });
        return {
            room,
            url: this.options.roomUrl(roomId),
            members,
            mode: this.mode(members),
            turns: this.store.turns(roomId),
            runs: this.store.runs(roomId),
        };
    }
    mode(members) {
        const roles = new Set(members.map((member) => member.role));
        return roles.has('chair') && roles.has('critic') && roles.has('judge')
            ? 'council'
            : 'debate';
    }
    /** The standing council room every door lands in. Created once. */
    ensureCouncil() {
        const existing = this.store.bySlug(COUNCIL_SLUG);
        if (existing)
            return existing;
        const dots = this.options.dots();
        const ids = ['Zeus', 'Nemesis', 'Themis'].map((name) => dots.find((dot) => dot.name === name)?.id);
        if (ids.some((id) => !id))
            return undefined;
        const room = this.createRoom('RIG Council', ids);
        this.store.setSlug(room.id, COUNCIL_SLUG);
        return this.store.room(room.id);
    }
    /** Accepts a human prompt and starts the debate in the background. */
    post(roomId, text, options = {}) {
        this.store.room(roomId);
        if (this.options.paused())
            throw new Error('Room agents are paused.');
        // A run still awaiting a verdict stays open (fix 1), but it must not
        // deadlock the room: a new prompt starts a fresh debate while the old run
        // keeps its open record until someone lands a verdict on it.
        if (this.store.runs(roomId).some((run) => run.status === 'running'))
            throw new Error('Room is already debating. Wait for the verdict.');
        // Fix 4 (Mike, 2026-10-06): a debate run requires an evidence pack at
        // creation. No pack, the room refuses to start and says why - episode 2
        // drifted exactly because the room debated with no Birch evidence.
        const packCalls = options.evidence === false
            ? []
            : (options.evidence ?? this.options.evidence?.(text, roomId) ?? []);
        if (!packCalls.length)
            throw new Error('No evidence pack: this room will not debate without one. Pass an evidence pack (read-only bridge calls) when you create the run.');
        const run = this.store.startRun(roomId);
        this.store.updateRun(run.id, {
            protocol: options.protocol ?? 'council2',
            tier: options.tier ?? this.options.defaultTier ?? 'frontier',
        });
        this.store.addTurn({
            roomId,
            runId: run.id,
            dotId: null,
            // Same label from every door: the prompt the Dots see must not depend
            // on which door it came through, or the doors drift.
            speaker: 'Mike',
            role: 'human',
            content: text,
            model: null,
            saw: [],
        });
        const controller = new AbortController();
        this.controllers.set(run.id, controller);
        const done = this.debate(roomId, run.id, text, controller.signal, options)
            .catch((error) => {
            this.store.updateRun(run.id, {
                status: 'failed',
                stage: 'failed',
                error: error instanceof Error ? error.message : 'Debate failed.',
                endedAt: Date.now(),
            });
        })
            .finally(() => this.controllers.delete(run.id));
        return { run, done };
    }
    /**
     * Seat tool call (Ultraplan S1, 2026-10-05). The seat policy in
     * ~/.rig/opendots-experts/seats decides HERE, before any bridge call: a chair,
     * judge or critic is a coordinator seat and may not write, send, spend, delete
     * or execute. The room stays advisory by doctrine - this is the governed door a
     * caller uses on a seat's behalf - and every answer is logged as a turn, so a
     * refusal is as auditable as a success.
     */
    async seatTool(roomId, dotId, call) {
        const member = this.store.members(roomId).find((m) => m.dotId === dotId);
        if (!member)
            throw new Error('That Dot is not a member of this room.');
        const seat = seatForRole(member.role);
        const tool = `${call.server}/${call.tool}`;
        const verdict = classifySeatTool(seat, tool);
        const who = this.options.dots().find((d) => d.id === dotId)?.name ?? dotId;
        if (!verdict.allowed) {
            const turn = this.store.addTurn({
                roomId,
                runId: null,
                dotId,
                speaker: 'Seat policy',
                role: 'system',
                content: `${who} is a ${member.role} seat (${seat}) and may not call ${tool}: ${verdict.reason} Nothing was called.`,
                model: null,
                saw: [],
                phase: 'triage',
                meta: {
                    seatRefusal: {
                        seat,
                        role: member.role,
                        cls: verdict.cls,
                        tool,
                        policySource: describeSeatPolicy(seat).source,
                    },
                },
            });
            return { allowed: false, verdict, turnId: turn.id };
        }
        const run = this.options.callSeatTool ?? callBridge;
        const started = Date.now();
        let result;
        try {
            result = await run(call, { room: roomId });
        }
        catch (error) {
            result = {
                ok: false,
                error: error instanceof Error ? error.message : String(error),
            };
        }
        const turn = this.store.addTurn({
            roomId,
            runId: null,
            dotId,
            speaker: who,
            role: member.role,
            content: result.ok
                ? `Called ${tool} as a ${seat} seat (${verdict.cls}). Receipt ${result.receipt ?? 'none'}.`
                : `Called ${tool} as a ${seat} seat (${verdict.cls}) and it failed: ${result.error ?? result.denied ?? 'no reason given'}.`,
            model: null,
            saw: [],
            phase: 'triage',
            meta: {
                seatCall: {
                    seat,
                    role: member.role,
                    cls: verdict.cls,
                    tool,
                    ok: result.ok,
                    receipt: result.receipt,
                    ms: result.ms ?? Date.now() - started,
                    error: result.error,
                    denied: result.denied,
                },
                ...(result.receipt ? { receipts: [result.receipt] } : {}),
            },
        });
        return { allowed: true, verdict, result, turnId: turn.id };
    }
    abortAll() {
        for (const controller of this.controllers.values())
            controller.abort();
    }
    persona(dot) {
        if (!dot)
            return '';
        // Persona only: the Dot's own instructions, trimmed. Room rules win.
        // Seat doctrine cards (team rooms) use the full stored instructions; dotSchema caps them at 2000.
        // (patch-rooms-persona-budget.diff, applied 2026-10-05 by octop-build lane sM5i3UBs1UO95Ypo)
        return `You are ${dot.name}. Your standing role:\n${dot.instructions.slice(0, 2000)}`;
    }
    transcript(roomId, runId, fresh) {
        const turns = this.store.turns(roomId);
        const earlier = fresh
            ? []
            : turns.filter((turn) => turn.runId !== runId).slice(-8);
        const current = turns.filter((turn) => turn.runId === runId);
        const render = (list) => list.map((turn) => `${turn.speaker}: ${turn.content}`).join('\n\n');
        return {
            ids: [...earlier, ...current].map((turn) => turn.id),
            text: (earlier.length
                ? `Earlier in this room:\n${render(earlier)}\n\n---\n`
                : '') + `This round so far:\n${render(current)}`,
        };
    }
    async speak(roomId, runId, dot, role, directive, signal, fresh = false, evidence) {
        const name = dot?.name ?? 'Dot';
        this.store.updateRun(runId, { stage: `${name} is speaking` });
        const context = this.transcript(roomId, runId, fresh);
        const messages = [
            {
                role: 'system',
                content: [this.persona(dot), DOCTRINE, directive]
                    .filter(Boolean)
                    .join('\n\n'),
            },
            {
                role: 'user',
                content: `${evidence
                    ? `EVIDENCE (read-only; cite the ids like (rcpt_0123abcd45)):\n${evidence.text}\n\n`
                    : ''}${context.text}\n\nNow it is your turn, ${name}. Speak only as ${name}; do not write lines for other speakers.`,
            },
        ];
        const complete = this.options.complete ?? chatComplete;
        const answer = await complete(this.options.routes(), messages, {
            maxTokens: 320,
            // Greedy decoding: the same problem gives the same debate through any
            // door (browser or CLI), so the doors cannot drift apart.
            temperature: 0,
            disableThinking: this.options.disableThinking,
            signal,
        });
        const raw = answer.content
            .replace(new RegExp(`^\\**${name}\\**\\s*:\\s*`, 'i'), '')
            .trim();
        // Fix 2 (Mike's relay): a number in a seat turn with no evidence id in the
        // turn is struck - it leaves the transcript as "[struck: 5%]".
        const struck = strikeSeatNumbers(raw);
        const content = struck.content;
        const ungroundedNumbers = struck.struck;
        return this.store.addTurn({
            roomId,
            runId,
            dotId: dot?.id ?? null,
            speaker: name,
            role,
            content,
            model: answer.model,
            saw: context.ids,
            meta: ungroundedNumbers.length ? { ungroundedNumbers } : null,
        });
    }
    async debate(roomId, runId, problem, signal, options = {}) {
        // CODE rung (jev-everywhere L0): deterministic rules run before Jev and
        // before any seat speaks. A hit ends the run with no model call.
        const gate = this.options.gate?.(problem) ?? null;
        if (gate) {
            this.store.addTurn({
                roomId,
                runId,
                dotId: null,
                speaker: 'Gate',
                role: 'system',
                content: `Stopped by a deterministic rule before any model ran (${gate.id}, ${gate.action}). ${gate.reason}`,
                model: null,
                saw: [],
                phase: 'triage',
                meta: { codeGate: gate },
            });
            this.store.updateRun(runId, {
                triage: 'code',
                verdict: gate.action === 'hold' ? 'HOLD' : 'BLOCKED',
                move: null,
                status: 'done',
                stage: 'done',
                endedAt: Date.now(),
            });
            return;
        }
        const members = this.store.members(roomId);
        if (this.mode(members) === 'council')
            return (options.protocol ?? 'council2') === 'classic'
                ? this.council(roomId, runId, problem, members, signal, options)
                : this.council2(roomId, runId, problem, members, signal, options);
        const fresh = !!options.fresh;
        // Fix 4 (Mike 2026-10-06): one evidence pack per debate, attached before
        // any seat speaks - the ep2 drift happened because the room had none.
        const human = this.store
            .turns(roomId)
            .filter((turn) => turn.runId === runId)
            .map((turn) => turn.id);
        const ev = await this.evidencePack(roomId, runId, problem, options, human);
        // Open debate: each member answers in order, and every speaker after the
        // first must take a position on a named earlier speaker.
        const order = members.map((member) => this.dot(member.dotId));
        for (const [index, dot] of order.entries()) {
            if (!dot)
                continue;
            const previous = order[index - 1]?.name;
            await this.speak(roomId, runId, dot, 'member', index === 0
                ? 'Open the debate: take a clear position on the problem and name one concrete move. Under 90 words.'
                : `Respond to ${previous} by name: say which specific claim you dispute or would change, and why, then give your own move. Under 90 words.`, signal, fresh, ev);
        }
        // Fix 1 (Mike 2026-10-06): every debate ends in a structured verdict -
        // decision, confidence, the top dissent preserved. The judge if the room
        // has one, else the chair (the producer, for team rooms). This path used
        // to close with no verdict at all, which is exactly the core-loop failure.
        const verdictMember = members.find((member) => member.role === 'judge') ??
            members.find((member) => member.role === 'chair') ??
            members[0];
        const verdictDot = this.dot(verdictMember?.dotId);
        const verdictDirective = 'Issue the final verdict on this round. Format, exactly: first a line "CONFIDENCE: high|medium|low", then a line "DISSENT: <the strongest objection you did not resolve>", then the last line "VERDICT: APPROVE|REJECT|REJECT pending evidence: <the concrete move>". Every number in the verdict must carry an evidence id from the EVIDENCE block in the same sentence, like 6,380 (rcpt_0123abcd45) - a number with no evidence id is struck and cannot appear in the verdict. Keep it under 90 words.';
        if (verdictDot) {
            const turn = await this.speak(roomId, runId, verdictDot, 'judge', verdictDirective, signal, fresh, ev);
            let gate = gateVerdict(turn.content, ev?.text);
            if (!gate.structured) {
                const retry = await this.speak(roomId, runId, verdictDot, 'judge', `${verdictDirective}\n\nYour last turn was not a structured verdict. Write the verdict again in the exact format now.`, signal, fresh, ev);
                gate = gateVerdict(retry.content, ev?.text);
            }
            if (!gate.structured) {
                // Fix 1: no verdict = the run stays open, never a silent done/UNCLEAR.
                this.store.updateRun(runId, {
                    verdict: null,
                    move: null,
                    status: 'awaiting-verdict',
                    stage: 'awaiting a structured verdict (decision + confidence + dissent)',
                    endedAt: Date.now(),
                });
                return;
            }
            this.store.updateRun(runId, {
                verdict: gate.verdict,
                move: gate.move,
                status: 'done',
                stage: 'done',
                endedAt: Date.now(),
            });
            return;
        }
        this.store.updateRun(runId, {
            status: 'done',
            stage: 'done',
            endedAt: Date.now(),
        });
    }
    resolveWorker(zeusText, members, chair) {
        const excluded = new Set(members
            .filter((member) => member.role !== 'worker')
            .map((member) => member.dotId));
        const roomWorkers = members
            .filter((member) => member.role === 'worker')
            .map((member) => this.dot(member.dotId))
            .filter((dot) => !!dot);
        const roster = this.roster(members, chair);
        const assigned = zeusText.match(/ASSIGN\s*:\s*\**\s*([^\n*.,;]+)/i)?.[1];
        const candidates = [...roomWorkers, ...roster];
        if (assigned) {
            const wanted = assigned.trim().toLowerCase();
            const hit = candidates.find((dot) => dot.name.toLowerCase() === wanted) ??
                candidates.find((dot) => wanted.includes(dot.name.toLowerCase()) ||
                    dot.name.toLowerCase().includes(wanted));
            if (hit && !excluded.has(hit.id))
                return hit;
        }
        return roomWorkers[0] ?? roster[0];
    }
    roster(members, chair) {
        const primes = new Set(members
            .filter((member) => member.role !== 'worker')
            .map((member) => member.dotId));
        const roomWorkerIds = members
            .filter((member) => member.role === 'worker')
            .map((member) => member.dotId);
        const spaceIds = new Set(chair?.spaceIds ?? []);
        const all = this.options.dots();
        const pool = all.filter((dot) => !primes.has(dot.id) &&
            (roomWorkerIds.includes(dot.id) ||
                dot.spaceIds.some((id) => spaceIds.has(id))) &&
            defaultRole(dot.name) === 'worker');
        return pool;
    }
    async council(roomId, runId, problem, members, signal, options = {}) {
        const fresh = !!options.fresh;
        const byRole = (role) => this.dot(members.find((member) => member.role === role).dotId);
        const chair = byRole('chair');
        const critic = byRole('critic');
        const judge = byRole('judge');
        const roster = this.roster(members, chair)
            .slice(0, 40)
            .map((dot) => `- ${dot.name}: ${dot.instructions.replace(/\s+/g, ' ').slice(0, 80)}`)
            .join('\n');
        // 1. Zeus assigns.
        const zeus = await this.speak(roomId, runId, chair, 'chair', `You chair this council. Name ONE concrete internal move that solves Mike's problem and assign ONE worker to carry it.
First line exactly: ASSIGN: <worker name from the roster>
Then at most two sentences: the move, and what you need the worker to answer.
Roster:
${roster}`, signal, fresh);
        // 2. The named worker answers, seeing Zeus.
        const worker = this.resolveWorker(zeus.content, members, chair);
        if (!worker)
            throw new Error('Zeus named no worker and the roster is empty.');
        if (!members.some((member) => member.dotId === worker.id))
            this.store.addMember(roomId, worker.id, 'worker');
        this.store.updateRun(runId, { worker: worker.name });
        await this.speak(roomId, runId, worker, 'worker', `Zeus assigned this to you. Answer it: how you would carry the move, the first concrete step, and what done looks like. Disagree with Zeus by name if his move is wrong. Under 100 words.`, signal, fresh);
        // 3. Nemesis attacks the answer.
        await this.speak(roomId, runId, critic, 'critic', `Attack ${worker.name}'s answer. Name its weakest specific claim and why it fails. If the move fails, write "BETTER MOVE: <move>". If it survives your attack, write "HOLDS IF: <one condition>". Under 80 words.`, signal, fresh);
        // 4. Themis returns one verdict; a bare no is retried once, then reported.
        const judgeDirective = `Return ONE verdict on this round.
First line exactly one of:
APPROVE: <the move to run now>
REJECT: <reason> | MOVE: <the safe internal move to run instead>
Start from APPROVE. If the plan is weak, rewrite it and APPROVE the rewrite, taking the better move from Nemesis if it is better. REJECT only if the only available move would send, post, spend, submit, or touch a minor. A bare no is a failure. After the first line, at most two sentences naming whose argument won.
After that, two more lines exactly: CONFIDENCE: <high|med|low or 0.0-1.0> and DISSENT: <the strongest objection you overruled; write "none recorded" if there is none>. Every number in this verdict must carry its evidence id in parentheses, e.g. 43% (rcpt_0123abcd45); a number without one is struck and the verdict becomes REJECT pending evidence.`;
        let verdictTurn = await this.speak(roomId, runId, judge, 'judge', judgeDirective, signal, fresh);
        let gate = gateVerdict(verdictTurn.content);
        if (!gate.structured) {
            verdictTurn = await this.speak(roomId, runId, judge, 'judge', `${judgeDirective}\nYour previous line was not a structured verdict. Fix it: first line APPROVE: <move> or REJECT: <reason> | MOVE: <safe move>, then CONFIDENCE: <value> and DISSENT: <objection>.`, signal, fresh);
            gate = gateVerdict(verdictTurn.content);
        }
        // Fix 1 + 2 (Mike, 2026-10-06): no structured verdict -> the run stays
        // open (awaiting-verdict), never a silent UNCLEAR. Uncited numbers ->
        // "REJECT pending evidence".
        if (!gate.structured) {
            this.store.updateRun(runId, {
                verdict: null,
                move: null,
                status: 'awaiting-verdict',
                stage: 'awaiting a structured verdict (decision, confidence, dissent)',
            });
            return;
        }
        const verdict = gate.verdict;
        if ((options.handoff ?? 'drive') === 'none') {
            this.store.updateRun(runId, {
                verdict,
                move: gate.move,
                status: 'done',
                stage: 'done',
                endedAt: Date.now(),
            });
            return;
        }
        this.store.updateRun(runId, {
            verdict,
            move: gate.move,
            stage: 'judging with JEV',
        });
        await this.writeArtifact(roomId, runId, verdict, gate.move, worker.name, options);
    }
    // -------------------------------------------------------------------------
    // council2: the upgraded protocol. Sources (read in code, not README):
    //  - Blind, parallel first pass: karpathy/llm-council backend/council.py
    //    L8-21 (stage1 query_models_parallel); 0xNyk council-of-high-
    //    intelligence SKILL.md L294-299 ("Each member sees ONLY the problem").
    //  - Restate + alternative framing before analysis: coh SKILL.md L243-256.
    //  - Anonymized peer review: llm-council council.py L49-62 (Response A/B);
    //    coh SKILL.md L409-433. Rotated presentation order per reviewer is our
    //    addition (neither repo rotates; llm-council runs reviewers in parallel).
    //  - Anti-conformity directive: coh SKILL.md L441-447.
    //  - Dissent channel / counterfactual: coh SKILL.md L463-483; DEALBREAKER
    //    and Minority Report: coh L500-506, L522, L785-786.
    //  - Confidence-weighted stance tally: coh SKILL.md L518-521.
    //  - Chairman who did not deliberate, distinct model: coh L265; llm-council
    //    council.py L115-157 (stage3 chairman synthesis).
    //  - Verdict sections Kill Criteria / Concrete Next Step / Unknowns: coh
    //    L753-763. Deviation on purpose: coh hands a split back to the user
    //    (L523); Mike's rule is "the recommendation, not the minutes", so the
    //    chairman always commits to one move and the split goes in the
    //    minority report.
    ladderFor(tier, seat, estTokens = 0) {
        return this.options.ladder
            ? this.options.ladder(tier, seat, estTokens)
            : seatLadder(tier, seat, {}, estTokens);
    }
    async askSeat(args) {
        const name = args.speaker ?? args.dot?.name ?? 'Dot';
        const complete = this.options.complete ?? chatComplete;
        // G7 (2026-10-15): size the prompt before choosing routes, so a
        // council-sized turn never lands on the single-slot :8111 companion.
        const messages = [
            { role: 'system', content: args.system },
            { role: 'user', content: args.user },
        ];
        const routes = this.ladderFor(args.tier, args.seat, estimateTokens(messages));
        const answer = await complete(routes, messages, {
            maxTokens: args.maxTokens ?? (args.tier === 'frontier' ? 2000 : 700),
            temperature: 0,
            disableThinking: this.options.disableThinking,
            signal: args.signal,
            timeoutMs: args.tier === 'frontier' ? 150_000 : 90_000,
        });
        const family = routes.find((route) => route.model === answer.model)?.family;
        const raw = answer.content
            .replace(new RegExp(`^\\**${name}\\**\\s*:\\s*`, 'i'), '')
            .trim();
        const cites = checkCitations(raw, args.receipts ?? []);
        // Fix 2: a number in a seat turn with no evidence id in the turn is struck
        // from the transcript (and the verdict is labeled REJECT pending evidence).
        const struck = strikeSeatNumbers(raw);
        const content = struck.content;
        const ungroundedNumbers = struck.struck;
        const turn = this.store.addTurn({
            roomId: args.roomId,
            runId: args.runId,
            dotId: args.dot?.id ?? null,
            speaker: name,
            role: args.role,
            content,
            model: answer.model,
            saw: args.saw,
            phase: args.phase,
            meta: {
                tried: answer.tried,
                usage: answer.usage ?? null,
                label: args.label,
                family,
                ...(args.receipts?.length ? { receipts: args.receipts } : {}),
                ...(cites.cited.length ? { cited: cites.cited } : {}),
                ...(cites.bad.length ? { badCites: cites.bad } : {}),
                ...(cites.unbacked ? { unbackedClaim: true } : {}),
                ...(ungroundedNumbers.length ? { ungroundedNumbers } : {}),
            },
        });
        return turn;
    }
    async chooseWorker(problem, members, chair) {
        const roomWorkers = members
            .filter((member) => member.role === 'worker')
            .map((member) => this.dot(member.dotId))
            .filter((dot) => !!dot);
        if (roomWorkers.length)
            return { dot: roomWorkers[0], how: 'room member' };
        const roster = this.roster(members, chair);
        if (!roster.length)
            return { dot: undefined, how: 'empty roster' };
        // Picking a worker from a fixed roster is a typed judgment: Jev first.
        const picked = await this.options
            .pickWorker?.(problem, roster.map((dot) => ({
            name: dot.name,
            about: dot.instructions.replace(/\s+/g, ' ').slice(0, 160),
        })))
            .catch(() => undefined);
        const hit = picked
            ? roster.find((dot) => dot.name.toLowerCase() === picked.toLowerCase())
            : undefined;
        if (hit)
            return { dot: hit, how: 'Jev choice' };
        // Jev unavailable: deterministic code, not a guess. Word overlap between
        // the problem and each Dot's standing instructions.
        const words = new Set(problem
            .toLowerCase()
            .split(/[^a-z0-9]+/)
            .filter((word) => word.length > 3));
        const scored = roster
            .map((dot) => ({
            dot,
            score: dot.instructions
                .toLowerCase()
                .split(/[^a-z0-9]+/)
                .filter((word) => words.has(word)).length,
        }))
            .sort((a, b) => b.score - a.score);
        return {
            dot: scored[0].dot,
            how: 'word-overlap fallback (Jev unavailable)',
        };
    }
    /** Build the evidence pack once and log it as a system turn whose meta
     *  carries the receipts. Returns undefined when there is nothing to fetch
     *  (no default and none posted), so tests and classic rooms are unchanged. */
    async evidencePack(roomId, runId, problem, options, human) {
        const calls = options.evidence === false
            ? []
            : (options.evidence ?? this.options.evidence?.(problem, roomId) ?? []);
        if (!calls.length)
            return undefined;
        this.store.updateRun(runId, {
            stage: `Evidence pack: ${calls.length} read-only call(s) through the bridge`,
        });
        const scope = options.evidenceScope ?? 'first';
        const each = options.evidenceMaxChars ?? 12000;
        const build = this.options.buildEvidence ?? buildEvidencePack;
        const t0 = Date.now();
        const pack = await build(calls, {
            room: roomId,
            maxCharsEach: each,
            maxTotalChars: each * 3,
        });
        const ms = Date.now() - t0;
        const receipts = pack.results
            .filter((r) => r.ok && r.receipt)
            .map((r) => r.receipt);
        const turn = this.store.addTurn({
            roomId,
            runId,
            dotId: null,
            speaker: 'Tool bridge',
            role: 'system',
            content: pack.text,
            model: null,
            saw: human,
            phase: 'evidence',
            meta: { receipts, evidenceChars: pack.text.length, evidenceMs: ms },
        });
        return { text: pack.text, index: pack.index, receipts, scope, turnId: turn.id };
    }
    async council2(roomId, runId, problem, members, signal, options = {}) {
        const tier = options.tier ?? this.options.defaultTier ?? 'frontier';
        const byRole = (role) => this.dot(members.find((member) => member.role === role).dotId);
        const chair = byRole('chair');
        const critic = byRole('critic');
        const judge = byRole('judge');
        const human = this.store
            .turns(roomId)
            .filter((turn) => turn.runId === runId)
            .map((turn) => turn.id);
        // 0. Triage (jev-everywhere: a fixed answer set is a typed judgment).
        this.store.updateRun(runId, { stage: 'Jev triage: debate or typed?' });
        const triage = this.options.triage
            ? await this.options.triage(problem).catch(() => ({
                kind: 'unavailable',
            }))
            : { kind: 'unavailable' };
        this.store.updateRun(runId, { triage: triage.kind });
        if (triage.kind === 'typed' && triage.answer) {
            this.store.addTurn({
                roomId,
                runId,
                dotId: null,
                speaker: 'Jev',
                role: 'system',
                content: `This is a typed judgment, not a debate: the answer set is fixed (${(triage.options ?? []).join(' / ')}). Jev's answer: ${triage.answer}.${triage.note ? ` ${triage.note}` : ''} No council was convened.`,
                model: 'jev',
                saw: human,
                phase: 'triage',
                meta: null,
            });
            this.store.updateRun(runId, {
                verdict: 'TYPED',
                move: triage.answer,
                status: 'done',
                stage: 'done',
                endedAt: Date.now(),
            });
            return;
        }
        const triageNote = triage.kind === 'unavailable'
            ? 'Jev triage unavailable: deferred to a full debate.'
            : triage.note
                ? `Jev triage: debate. ${triage.note}`
                : 'Jev triage: needs a debate (no fixed answer set).';
        this.store.addTurn({
            roomId,
            runId,
            dotId: null,
            speaker: 'Jev',
            role: 'system',
            content: triageNote,
            model: triage.kind === 'unavailable' ? null : 'jev',
            saw: human,
            phase: 'triage',
            meta: null,
        });
        const { dot: worker, how } = await this.chooseWorker(problem, members, chair);
        if (!worker)
            throw new Error('Room has no worker and the roster is empty.');
        if (!members.some((member) => member.dotId === worker.id))
            this.store.addMember(roomId, worker.id, 'worker');
        this.store.updateRun(runId, { worker: worker.name });
        // 0b. Evidence pack: fetched ONCE, before the first round, by the room's
        //     read-only tool bridge. Seats never call tools; they can only cite
        //     a receipt id that is in this pack (DOCTRINE).
        const ev = await this.evidencePack(roomId, runId, problem, options, human);
        const evFull = ev ? `\n\n${ev.text}` : '';
        const evIndex = ev
            ? `\n\n${ev.scope === 'all' ? ev.text : ev.index}`
            : '';
        const evSaw = ev ? [ev.turnId] : [];
        const receipts = ev?.receipts ?? [];
        const seats = [
            {
                dot: chair,
                seat: 'chair',
                role: 'chair',
                lens: 'You are the strategist. Find the move that removes the root cause, not the symptom.',
            },
            {
                dot: worker,
                seat: 'worker',
                role: 'worker',
                lens: `You are the executor (picked by ${how}). Say exactly how this gets done on this machine: files, commands, checks.`,
            },
            {
                dot: critic,
                seat: 'critic',
                role: 'critic',
                lens: 'You are the adversary. Run a premortem: assume the obvious fix fails in a week. Why? Then give the move that survives that.',
            },
        ];
        // 1. Blind, parallel. Nobody sees anyone else; this is what stops the
        //    whole room anchoring on whoever speaks first.
        this.store.updateRun(runId, {
            stage: `Blind first pass: ${seats.map((s) => s.dot?.name).join(', ')} thinking in parallel`,
        });
        const blindFormat = `Answer in this exact format, under 220 words:
RESTATE: <the real problem in one sentence>
REFRAME: <one alternative framing the question may have missed>
MOVE: <one concrete internal move; not a menu>
OWNER: <who executes it: Aside, OMP, a named Dot, or Mike>
WHY: <2-3 sentences; tag each claim [empirical|mechanistic|strategic|heuristic]>
RISK: <the most likely way this move fails>
STANCE: <3-6 word label for your move> | CONFIDENCE: high|med|low`;
        const blind = await Promise.all(seats.map((s) => this.askSeat({
            roomId,
            runId,
            dot: s.dot,
            role: s.role,
            phase: 'blind',
            system: [this.persona(s.dot), DOCTRINE, s.lens].join('\n\n'),
            user: `Problem from Mike:\n${problem}${evFull}\n\nYou are answering independently; you cannot see the other council members.\n\n${blindFormat}`,
            tier,
            seat: s.seat,
            signal,
            saw: [...human, ...evSaw],
            receipts,
        })));
        // 2. Anonymized cross-examination, parallel, presentation order rotated
        //    per reviewer so no position always sits first (position bias).
        const labels = blind.map((_, index) => `Member ${String.fromCharCode(65 + index)}`);
        this.store.updateRun(runId, {
            stage: 'Cross-examination: anonymized, rotated order, in parallel',
        });
        const cross = await Promise.all(seats.map((s, reviewer) => {
            const order = blind.map((_, i) => (i + reviewer) % blind.length);
            const shown = order
                .map((i) => `${labels[i]}:\n${blind[i].content}`)
                .join('\n\n---\n\n');
            return this.askSeat({
                roomId,
                runId,
                dot: s.dot,
                role: s.role,
                phase: 'cross',
                system: [this.persona(s.dot), DOCTRINE, s.lens].join('\n\n'),
                user: `Problem from Mike:\n${problem}${evIndex}\n\nIdentity is masked. These are the council's independent answers, labeled ${labels.join(', ')}. One of them is your own. Judge by argument quality, not by source, and do not guess identities.\n\n${shown}\n\nAnti-conformity directive: if your position was correct, defend it. Do not update because others disagree or because a view is repeated. Update only when a specific flaw in your reasoning is exposed, and name that flaw when you do.\n\nAnswer in this exact format, under 220 words:
STRONGEST: <label> - <the single most serious weakness in the STRONGEST answer, not a nitpick>
WEAKEST: <label> - <why it fails>
UPDATE: <kept or changed, and the specific flaw if changed>
MOVE: <your move now>
STANCE: <3-6 word label> | CONFIDENCE: high|med|low | DEALBREAKER: yes|no`,
                tier,
                seat: s.seat,
                signal,
                saw: [...blind.map((turn) => turn.id), ...evSaw],
                label: labels[reviewer],
                receipts,
            });
        }));
        // 3. Dissent channel. A minority answer must survive to the verdict, so
        //    unless someone already called a dealbreaker, the critic argues the
        //    strongest case against the emerging majority.
        const stances = cross.map((turn, i) => ({
            who: seats[i].dot?.name ?? '?',
            ...parseStance(turn.content),
        }));
        const tally = tallyStances(stances);
        let dissent;
        if (!stances.some((stance) => stance.dealbreaker)) {
            this.store.updateRun(runId, {
                stage: 'Dissent channel: Nemesis argues the other side',
            });
            dissent = await this.askSeat({
                roomId,
                runId,
                dot: critic,
                role: 'critic',
                phase: 'dissent',
                system: [this.persona(critic), DOCTRINE].join('\n\n'),
                user: `Problem from Mike:\n${problem}${evIndex}\n\nCross-examination so far:\n${cross
                    .map((turn, i) => `${seats[i].dot?.name}: ${turn.content}`)
                    .join('\n\n')}\n\nAssume the current majority is wrong. What is the strongest alternative, and what observable evidence would flip the decision? Under 150 words. End with: DEALBREAKER: yes|no`,
                tier,
                seat: 'critic',
                signal,
                saw: [...cross.map((turn) => turn.id), ...evSaw],
                receipts,
            });
        }
        // 4. Chairman verdict. Themis did not deliberate; she sees the named
        //    transcript and commits to ONE move.
        this.store.updateRun(runId, {
            stage: `${judge?.name ?? 'Judge'} is writing the verdict`,
        });
        const named = (phase, list) => list
            .map((turn) => `[${phase}] ${turn.speaker} (${turn.model}): ${turn.content}`)
            .join('\n\n');
        const transcript = [
            named('blind', blind),
            named('cross', cross),
            dissent ? named('dissent', [dissent]) : '',
        ]
            .filter(Boolean)
            .join('\n\n');
        const verdictFormat = `Output exactly these lines, under 300 words:
VERDICT: APPROVE: <the one move to run now>   (or: REJECT: <reason> | MOVE: <the safe internal move instead>)
OWNER: <the named agent that executes it>
FIRST STEP: <the first concrete action, specific enough to run>
WHY THIS WON: <name whose argument won and the strongest objection it survived>
CONFIDENCE: <high|med|low or 0.0-1.0>
MINORITY REPORT: <the strongest dissent, stated fairly; say if it was a dealbreaker>
KILL CRITERIA: If <observable> by <when>, this verdict is wrong and we <do what>.
UNKNOWNS: <what the council does not know>
Every number in this verdict must carry its evidence id in parentheses, e.g. 43% (rcpt_0123abcd45). A number without one is struck and the verdict becomes REJECT pending evidence.`;
        const judgeSystem = [
            this.persona(judge),
            DOCTRINE,
            'You are the chairman. You did not deliberate. Weigh arguments by validity, not by repetition or seniority. A menu fails: commit to one move. Start from APPROVE; if the plan is weak, rewrite it and APPROVE the rewrite. REJECT only if the only available move would send, post, spend, submit, or touch a minor. A bare no fails.',
        ].join('\n\n');
        let verdictTurn = await this.askSeat({
            roomId,
            runId,
            dot: judge,
            role: 'judge',
            phase: 'verdict',
            system: judgeSystem,
            user: `Problem from Mike:\n${problem}${evIndex}\n\nStance tally (confidence-weighted, high=1, med=0.75, low=0.5):\n${tally}\n\nTranscript:\n${transcript}\n\n${verdictFormat}`,
            tier,
            seat: 'judge',
            signal,
            saw: [
                ...[...blind, ...cross, ...(dissent ? [dissent] : [])].map((turn) => turn.id),
                ...evSaw,
            ],
            receipts,
        });
        // Fix 1 (Mike, 2026-10-06): parseVerdict never matched council2's
        // mandated "VERDICT: APPROVE:" first line, so runs ended verdict=null even
        // after a forced verdict. The gate parses both formats and demands the full
        // structure: decision, confidence, and the top dissent preserved.
        let gate = gateVerdict(verdictTurn.content, ev?.text);
        if (!gate.structured) {
            verdictTurn = await this.askSeat({
                roomId,
                runId,
                dot: judge,
                role: 'judge',
                phase: 'verdict',
                system: judgeSystem,
                receipts,
                user: `Your verdict is not structured. Start with "VERDICT: APPROVE: <move>" or "VERDICT: REJECT: <reason> | MOVE: <safe move>", then give CONFIDENCE: <value> and MINORITY REPORT: <the strongest dissent>. Every number needs its evidence id in parentheses. Rewrite it.\n\nPrevious:\n${verdictTurn.content}\n\n${verdictFormat}`,
                tier,
                seat: 'judge',
                signal,
                saw: [verdictTurn.id],
            });
            gate = gateVerdict(verdictTurn.content, ev?.text);
        }
        // No structured verdict -> the run stays open, not done (fix 1). Uncited
        // numbers -> "REJECT pending evidence" (fix 2).
        if (!gate.structured) {
            this.store.updateRun(runId, {
                verdict: null,
                move: null,
                status: 'awaiting-verdict',
                stage: 'awaiting a structured verdict (decision, confidence, dissent)',
            });
            return;
        }
        // Claim accuracy (hub SP4ikIin7S6GmLBw + relay xdjQtAGJmfSsidtm 2026-10-06,
        // aligned with the rig-wf gate node): every ranking, count or percentage
        // claim in the seat turns and the verdict is re-derived by code from the
        // evidence pack its line cites. A contradiction, or a claim with no
        // citation, forces "REJECT pending evidence" - the delivery lists each one.
        const claims = [
            ...(gate.claims ?? []),
            ...checkClaims([...blind, ...cross, ...(dissent ? [dissent] : [])]
                .map((turn) => `${turn.speaker}\n${turn.content}`)
                .join('\n'), ev?.text ?? ''),
        ];
        const rejectedClaims = claims.filter((claim) => claim.status === 'REJECTED');
        const verdict = gate.verdict;
        const KEYS = [
            'VERDICT',
            'OWNER',
            'FIRST STEP',
            'WHY THIS WON',
            // Fix 1 made CONFIDENCE a mandatory verdict line; the field parser must
            // know it or it gets swallowed into the previous section.
            'CONFIDENCE',
            'MINORITY REPORT',
            'KILL CRITERIA',
            'UNKNOWNS',
        ];
        // A field runs until the next KEY: line, so multi-line first steps and
        // unknown lists survive into the decision file.
        const field = (name) => {
            const lines = verdictTurn.content.split('\n');
            const start = lines.findIndex((line) => new RegExp(`^\\s*\\**${name}\\**\\s*:`, 'i').test(line));
            if (start < 0)
                return null;
            const out = [lines[start].replace(/^[^:]*:\s*/, '')];
            for (const line of lines.slice(start + 1)) {
                if (KEYS.some((key) => new RegExp(`^\\s*\\**${key}\\**\\s*:`, 'i').test(line)))
                    break;
                out.push(line);
            }
            return out.join('\n').trim() || null;
        };
        const all = [
            ...blind,
            ...cross,
            ...(dissent ? [dissent] : []),
            verdictTurn,
        ];
        const tokensIn = all.reduce((sum, turn) => sum + (turn.meta?.usage?.prompt ?? 0), 0);
        const tokensOut = all.reduce((sum, turn) => sum + (turn.meta?.usage?.completion ?? 0), 0);
        this.store.updateRun(runId, {
            verdict,
            move: gate.move,
            tokensIn,
            tokensOut,
        });
        if ((options.handoff ?? 'drive') === 'none') {
            this.store.updateRun(runId, {
                status: 'done',
                stage: 'done',
                endedAt: Date.now(),
            });
            return;
        }
        this.store.updateRun(runId, { stage: 'judging with JEV' });
        await this.writeArtifact(roomId, runId, verdict, gate.move, worker.name, options, {
            protocol: 'council2',
            tier,
            triage: triage.kind,
            owner: field('OWNER'),
            first_step: field('FIRST STEP'),
            why_this_won: field('WHY THIS WON'),
            confidence: field('CONFIDENCE'),
            minority_report: field('MINORITY REPORT'),
            kill_criteria: field('KILL CRITERIA'),
            unknowns: field('UNKNOWNS'),
            tally,
            models: all.map((turn) => ({
                speaker: turn.speaker,
                phase: turn.phase,
                model: turn.model,
                fell_back_from: turn.meta?.tried ?? [],
            })),
            tokens: { prompt: tokensIn, completion: tokensOut },
        });
    }
    /**
     * The one council-drive handoff. Contract kept from `rig-advice drive`:
     *   <stamp>-decision.json  {path:"decide", verdict, turns[], not_permission_to_send}
     *   <stamp>-task.json      {for, do, method, do_not, source, jev_verdict, jev_decision_id}
     *   latest-move.txt        "MOVE\n<Themis turn>\n\nMETHOD\n<json>\n"
     * plus additive fields (via, door, room_id, room_url, run_id, worker, move).
     * JEV: council.judgment via rig-s1gate. A task is handed off only on APPROVE
     * with a JEV verdict of PASS or ESCALATE; BLOCK or an unavailable judge
     * defers (AGENTS.md: classifier unavailable means defer, never guess).
     */
    async writeArtifact(roomId, runId, verdict, move, worker, options = {}, extra = {}) {
        const dir = this.options.councilDir ??
            join(homedir(), '.rig', 'live', 'council-drive');
        mkdirSync(dir, { recursive: true });
        let id = stamp();
        if (existsSync(join(dir, `${id}-decision.json`)))
            id = `${id}-${runId.slice(0, 8)}`;
        const decisionPath = join(dir, `${id}-decision.json`);
        const all = this.store.turns(roomId);
        const turns = all.filter((turn) => turn.runId === runId && turn.role !== 'human');
        const problem = all.find((turn) => turn.runId === runId && turn.role === 'human')
            ?.content ?? '';
        const decision = {
            path: 'decide',
            verdict,
            turns: turns.map((turn) => `${turn.speaker}: ${turn.content}`),
            not_permission_to_send: true,
            via: 'opendots-room',
            door: options.door ?? 'browser',
            room_id: roomId,
            room_url: this.options.roomUrl(roomId),
            run_id: runId,
            problem,
            worker,
            move,
            ...extra,
        };
        writeFileSync(decisionPath, JSON.stringify(decision, null, 2) + '\n');
        const judge = this.options.judge ??
            defaultJudge(this.options.s1gateBin ?? join(homedir(), '.rig', 'bin', 'rig-s1gate'));
        const jev = await judge(decisionPath, `council.drive:${id}`).catch(() => ({
            verdict: 'UNAVAILABLE',
            decision_id: undefined,
            enforced: undefined,
        }));
        let taskPath = null;
        const handOff = verdict === 'APPROVE' &&
            !!move &&
            (jev.verdict === 'PASS' || jev.verdict === 'ESCALATE');
        if (handOff) {
            const themis = decision.turns[decision.turns.length - 1];
            taskPath = join(dir, `${id}-task.json`);
            writeFileSync(taskPath, JSON.stringify({
                for: ['aside', 'omp'],
                do: themis,
                method: options.method ?? null,
                do_not: ['send', 'post', 'spend', 'submit'],
                source: decisionPath,
                jev_verdict: jev.verdict ?? null,
                jev_decision_id: jev.decision_id ?? null,
            }, null, 2) + '\n');
            writeFileSync(join(dir, 'latest-move.txt'), 'MOVE\n' +
                themis +
                '\n\nMETHOD\n' +
                JSON.stringify(options.method ?? null, null, 2) +
                '\n');
        }
        this.store.updateRun(runId, {
            status: 'done',
            stage: 'done',
            decisionPath,
            taskPath,
            jevVerdict: jev.verdict ?? null,
            // TEXT column: bind a string, or SQLite stores the REAL "175290.0".
            jevDecisionId: jev.decision_id === undefined || jev.decision_id === null
                ? null
                : String(jev.decision_id),
            jevEnforced: jev.enforced === undefined || jev.enforced === null
                ? null
                : jev.enforced
                    ? 1
                    : 0,
            endedAt: Date.now(),
        });
        return { decisionPath, taskPath, size: statSync(decisionPath).size };
    }
}
/** Parses "STANCE: label | CONFIDENCE: x | DEALBREAKER: y" (coh SKILL.md L500). */
export function parseStance(text) {
    const line = text.match(/STANCE\s*:\s*([^|\n]+)(?:\|\s*CONFIDENCE\s*:\s*(\w+))?(?:\s*\|\s*DEALBREAKER\s*:\s*(\w+))?/i);
    return {
        label: (line?.[1] ?? 'unstated').trim().toLowerCase(),
        confidence: (line?.[2] ?? 'med').toLowerCase(),
        dealbreaker: /^y/i.test(line?.[3] ?? ''),
    };
}
/** Confidence-weighted tally (coh SKILL.md L518-521): high 1, med .75, low .5. */
export function tallyStances(stances) {
    const weight = (c) => c.startsWith('h') ? 1 : c.startsWith('l') ? 0.5 : 0.75;
    const totals = new Map();
    for (const stance of stances) {
        const entry = totals.get(stance.label) ?? { w: 0, who: [] };
        entry.w += weight(stance.confidence);
        entry.who.push(`${stance.who} (${stance.confidence}${stance.dealbreaker ? ', DEALBREAKER' : ''})`);
        totals.set(stance.label, entry);
    }
    const bar = (2 / 3) * stances.length;
    return [...totals.entries()]
        .sort((a, b) => b[1].w - a[1].w)
        .map(([label, entry]) => `${label}: ${entry.w.toFixed(2)} of ${stances.length} (2/3 bar ${bar.toFixed(2)}${entry.w >= bar ? ', CLEARS' : ''}) - ${entry.who.join(', ')}`)
        .join('\n');
}
