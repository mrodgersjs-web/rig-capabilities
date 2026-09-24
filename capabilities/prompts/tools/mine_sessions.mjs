#!/usr/bin/env node
// mine_sessions.mjs - distill prompt-shaped user turns out of local agent session stores.
//
// READ-ONLY over every store it touches. Writes ONLY into dump/ (gitignored).
// Usage:
//   node tools/mine_sessions.mjs [--out dump/candidates.jsonl] [--top N] [--skip SESSION_ID_SUFFIX]
//
// Stores mapped (schemas verified on this machine 2026-09-23):
//   aside          ~/.aside/u/0/sessions/<date>_<id>/messages.jsonl   role user, content string
//   codex-rollout  ~/.codex/archived_sessions/rollout-*.jsonl          response_item / message / role user
//   codex-thread   ~/.codex/thread_history_1.sqlite                    thread_items item_type userMessage
//   codex-history  ~/.codex/history.jsonl                              session_id, ts (seconds), text
//   claude         ~/.claude/projects/<encoded>/<uuid>.jsonl           type user, message.content
//   promptfile     ~/.codex/commands, ~/.codex/prompts, ~/.rig/universal-commands, ~/.omp/commands
//
// OMP (Oh My Pi) is deliberately ABSENT: it keeps no chat transcripts on this machine
// (~/.omp/sessions is empty and ~/.omp/agent/sessions does not exist). Verified, not assumed.
//
// Honesty rules:
//   - injected system context arrives disguised as user turns and MUST be dropped
//     (AGENTS.md instruction blocks, environment context, context packets, tool wrappers)
//   - the drop-needles below are built from char codes on purpose: a literal wrapper tag in
//     this source gets rewritten by output sanitizers and would silently break the filter
//   - nothing here exports raw transcripts; candidates are individual prompt-shaped turns
//     with a store reference, and dump/ is gitignored so they never leave disk
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const HOME = os.homedir();
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const args = process.argv.slice(2);
function arg(n) { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined; }

const OUT = path.resolve(ROOT, arg('--out') || 'dump/candidates.jsonl');
const TOP = Number(arg('--top') || 25);
const SKIP = arg('--skip') || 'dOYCthsuZzjXt5qT'; // the live session by default

fs.mkdirSync(path.dirname(OUT), { recursive: true });
const out = fs.createWriteStream(OUT);

const stats = {};
function bump(store, key, n = 1) {
  stats[store] = stats[store] || { scanned: 0, extracted: 0, kept: 0, injected_skipped: 0, short_skipped: 0, errors: 0, error_detail: '' };
  stats[store][key] += n;
}

// System context arrives as fake user turns. Drop anything matching these.
const LT = String.fromCharCode(60); // left angle
const GT = String.fromCharCode(62); // right angle
const tagStart = (name) => new RegExp('^' + LT + name, 'm');
const wrapperStart = new RegExp('^\\[' + 'BEGIN' + '_UNTRUSTED' + '_TOOL' + '_OUTPUT', 'm');
// Machine envelopes arrive as angle-bracket tagged blocks and impersonate user turns.
// Each name below is a transport wrapper, not a human job. (char-code built: see header.)
const ENVELOPES = [
  'realtime_delegation', 'heartbeat', 'automation', 'readonly', 'subagent',
  'subagent_notification', 'in_app_browser', 'in_app_browser_context', 'turn_aborted',
  'local-command-caveat', 'skill', 'environment_context', 'system', 'request',
  'session_meta', 'transcript', 'handoff', 'goal_update',
];
const INJECTED = [
  /^#\s*AGENTS\.md instructions/m,
  /^Relevant skill docs are available/m,
  /^Caveat:/m,
  wrapperStart,
  /^## RIG OS-enforced verified context/m,
  /^ContextPacket:/m,
  /^# AGENTS\.md/m,
  /^\[Request interrupted/m,
  ...ENVELOPES.map(tagStart),
];
const isInjected = (t) => INJECTED.some((re) => re.test(t.trimStart()));

// Prompt shape: a real instruction, not a filename, not a novel.
const isPromptShaped = (t) => {
  const words = t.trim().split(/\s+/).length;
  return t.length >= 40 && t.length <= 4000 && words >= 6;
};

const seen = new Map(); // sha -> { count, stores:Set, refs:[], sample }
const norm = (t) => t.trim().replace(/\s+/g, ' ').toLowerCase();
const sha = (t) => crypto.createHash('sha256').update(norm(t)).digest('hex');

function keep(store, ref, ts, text) {
  if (typeof text !== 'string') return;
  const t = text.trim();
  if (!t) return;
  bump(store, 'extracted');
  if (isInjected(t)) return bump(store, 'injected_skipped');
  if (!isPromptShaped(t)) return bump(store, 'short_skipped');
  bump(store, 'kept');
  const h = sha(t);
  const prev = seen.get(h);
  if (prev) {
    prev.count++;
    prev.stores.add(store);
    if (prev.refs.length < 3) prev.refs.push(ref);
  } else {
    seen.set(h, { count: 1, stores: new Set([store]), refs: [ref], sample: t });
  }
  out.write(JSON.stringify({ store, ref, ts: ts || null, sha: h, chars: t.length, text: t }) + '\n');
}

function walkJsonlFiles(dir, depth = 0) {
  if (depth > 4) return [];
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return []; }
  const files = [];
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) files.push(...walkJsonlFiles(p, depth + 1));
    else if (e.isFile() && e.name.endsWith('.jsonl')) files.push(p);
  }
  return files;
}

function eachJsonLine(file, fn) {
  let raw;
  try { raw = fs.readFileSync(file, 'utf8'); } catch { return; }
  for (const line of raw.split('\n')) {
    if (!line.trim()) continue;
    let j;
    try { j = JSON.parse(line); } catch { continue; }
    fn(j);
  }
}

const textOf = (c) =>
  typeof c === 'string' ? c
  : Array.isArray(c) ? c.filter((p) => p && p.type === 'text').map((p) => p.text).join('\n')
  : '';

// ---------- aside ----------
function mineAside() {
  const base = path.join(HOME, '.aside/u/0/sessions');
  let dirs = [];
  try { dirs = fs.readdirSync(base); } catch { bump('aside', 'errors'); stats.aside.error_detail = 'sessions dir unreadable'; return; }
  for (const d of dirs) {
    if (d.includes(SKIP)) continue;
    bump('aside', 'scanned');
    const f = path.join(base, d, 'messages.jsonl');
    if (!fs.existsSync(f)) continue;
    eachJsonLine(f, (j) => {
      if (j.role !== 'user') return;
      keep('aside', 'sessions/' + d + '/messages.jsonl', j.timestamp, textOf(j.content));
    });
  }
}

// ---------- codex rollouts ----------
function mineCodexRollouts() {
  for (const base of [path.join(HOME, '.codex/archived_sessions'), path.join(HOME, '.codex/sessions')]) {
    const files = walkJsonlFiles(base);
    for (const f of files) {
      bump('codex-rollout', 'scanned');
      eachJsonLine(f, (j) => {
        if (j.type !== 'response_item') return;
        const p = j.payload || {};
        if (p.type !== 'message' || p.role !== 'user') return;
        const text = (p.content || []).filter((c) => c && (c.type === 'input_text' || c.type === 'text')).map((c) => c.text).join('\n');
        keep('codex-rollout', path.relative(HOME, f), j.timestamp, text);
      });
    }
  }
}

// ---------- codex thread sqlite ----------
function mineCodexThread() {
  const db = path.join(HOME, '.codex/thread_history_1.sqlite');
  if (!fs.existsSync(db)) { bump('codex-thread', 'errors'); stats['codex-thread'].error_detail = 'db absent'; return; }
  bump('codex-thread', 'scanned', 1);
  let rows = [];
  try {
    const res = execFileSync('sqlite3', [db, '-json',
      "SELECT thread_id, created_at_ms, item_json FROM thread_items WHERE item_type='userMessage' ORDER BY created_at_ms;"],
      { maxBuffer: 256 * 1024 * 1024 });
    rows = JSON.parse(res.toString('utf8') || '[]');
  } catch (e) {
    bump('codex-thread', 'errors');
    stats['codex-thread'].error_detail = String(e.message).slice(0, 200);
    return;
  }
  for (const r of rows) {
    let item;
    try { item = JSON.parse(r.item_json); } catch { continue; }
    keep('codex-thread', 'thread_items/' + r.thread_id, r.created_at_ms, textOf(item.content));
  }
}

// ---------- codex history.jsonl ----------
function mineCodexHistory() {
  const f = path.join(HOME, '.codex/history.jsonl');
  if (!fs.existsSync(f)) return;
  bump('codex-history', 'scanned', 1);
  eachJsonLine(f, (j) => keep('codex-history', 'history.jsonl/' + (j.session_id || 'unknown'), (j.ts || 0) * 1000, j.text));
}

// ---------- claude projects ----------
function mineClaude() {
  const base = path.join(HOME, '.claude/projects');
  const files = walkJsonlFiles(base);
  for (const f of files) {
    bump('claude', 'scanned');
    eachJsonLine(f, (j) => {
      if (j.type !== 'user') return;
      keep('claude', path.relative(HOME, f), j.timestamp, textOf(j.message && j.message.content));
    });
  }
}

// ---------- prompt files (already-curated corpora) ----------
function minePromptFiles() {
  const dirs = ['~/.codex/commands', '~/.codex/prompts', '~/.rig/universal-commands', '~/.omp/commands']
    .map((p) => p.replace('~', HOME));
  for (const dir of dirs) {
    let names = [];
    try { names = fs.readdirSync(dir); } catch { bump('promptfile', 'errors'); continue; }
    for (const n of names) {
      if (!n.endsWith('.md')) continue;
      const f = path.join(dir, n);
      bump('promptfile', 'scanned');
      let text;
      try { text = fs.readFileSync(f, 'utf8'); } catch { bump('promptfile', 'errors'); continue; }
      keep('promptfile', path.relative(HOME, f), null, text);
    }
  }
}

mineAside();
mineCodexRollouts();
mineCodexThread();
mineCodexHistory();
mineClaude();
minePromptFiles();
out.end();

// summary: what was found, what was dropped and why, never a bare total.
const summary = {
  generated: new Date().toISOString(),
  out: OUT,
  stores: stats,
  unique_prompts: seen.size,
  total_kept_records: Object.values(stats).reduce((a, s) => a + s.kept, 0),
};
const topRepeated = [...seen.entries()]
  .map(([h, v]) => ({ sha: h.slice(0, 12), count: v.count, stores: [...v.stores], refs: v.refs, chars: v.sample.length, text: v.sample }))
  .sort((a, b) => b.count - a.count)
  .slice(0, TOP);
fs.writeFileSync(path.join(path.dirname(OUT), 'top-repeated.jsonl'), topRepeated.map((r) => JSON.stringify(r)).join('\n') + '\n');
fs.writeFileSync(path.join(path.dirname(OUT), 'stats.json'), JSON.stringify({ ...summary, top_repeated_file: 'top-repeated.jsonl' }, null, 2) + '\n');

console.log(JSON.stringify(summary, null, 2));
console.log('top ' + TOP + ' repeated prompts -> ' + path.join(path.dirname(OUT), 'top-repeated.jsonl'));
