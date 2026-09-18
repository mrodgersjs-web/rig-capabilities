// lib.mjs — shared helpers for the RIG prompt library. Zero dependencies (Node >= 18).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REGISTRY_PATH = path.join(ROOT, 'registry.json');
export const LEDGER_PATH = path.join(ROOT, 'ledger.jsonl');
export const PROMPTS_DIR = path.join(ROOT, 'prompts');

export function sha256(content) {
  return crypto.createHash('sha256').update(content, 'utf8').digest('hex');
}

export function readRegistry() {
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
}

export function writeRegistry(reg) {
  reg.updated = new Date().toISOString().slice(0, 10);
  fs.writeFileSync(REGISTRY_PATH, JSON.stringify(reg, null, 2) + '\n');
}

export function readLedger() {
  const lines = fs.readFileSync(LEDGER_PATH, 'utf8').trim().split('\n').filter(Boolean);
  return lines.map((l) => JSON.parse(l));
}

// Hash-chained append: each entry hashes (prevHash + canonical payload), so any
// later edit or deletion of a past entry breaks the chain. Mirrors the
// rig-design-studio pull-ledger pattern.
export function appendLedger(entry) {
  const chain = readLedger();
  const prev = chain.length ? chain[chain.length - 1].hash : 'GENESIS';
  const { hash: _ignore, ...payload } = entry;
  const full = { ...entry, prev };
  const canonical = JSON.stringify({ ...payload, prev });
  full.hash = sha256(canonical);
  fs.appendFileSync(LEDGER_PATH, JSON.stringify(full) + '\n');
  return full;
}

export function promptDir(id) {
  return path.join(PROMPTS_DIR, id);
}

export function nextVersion(id) {
  const dir = promptDir(id);
  const vdir = path.join(dir, 'versions');
  if (!fs.existsSync(vdir)) return 1;
  const existing = fs.readdirSync(vdir).filter((f) => /^v\d+\.md$/.test(f));
  return existing.length + 1;
}

export function frontmatter(obj) {
  const lines = Object.entries(obj).map(([k, v]) => `${k}: ${v}`);
  return `---\n${lines.join('\n')}\n---\n`;
}

// Very small frontmatter parser (key: value lines only) for pull/list.
export function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { meta: {}, body: text };
  const meta = {};
  for (const line of m[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx > 0) meta[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
  }
  return { meta, body: text.slice(m[0].length) };
}
