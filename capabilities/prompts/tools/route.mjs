// route.mjs — deterministic lexical ranker over the prompt registry. Zero dependencies.
// Usage:
//   node tools/route.mjs "<the job as stated>" [--json] [--top N]
//   node tools/route.mjs --write-routing        # regenerate the skill routing table
//
// Honest scope: lexical match over registry fields (id, task, domain, category,
// triggers). No embeddings, no model, no network. Scores are relative within one
// registry snapshot; a low top score means NO_STORED_PROMPT, not a forced pick.
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, readRegistry, promptDir, PROMPTS_DIR, parseFrontmatter } from './lib.mjs';

const STOP = new Set(['the', 'a', 'an', 'and', 'or', 'to', 'of', 'for', 'in', 'on', 'with',
  'is', 'are', 'be', 'this', 'that', 'it', 'i', 'my', 'me', 'we', 'you', 'your', 'as',
  'at', 'by', 'from', 'into', 'up', 'out', 'want', 'need', 'please', 'can', 'could']);

const tokenize = (s) => (s || '').toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length > 1 && !STOP.has(w));

function docTokens(p) {
  return tokenize([p.id, p.task, p.domain, p.category, (p.triggers || []).join(' '), p.provenance].join(' '));
}

function rank(query, registry, top) {
  const q = tokenize(query);
  const docs = registry.prompts.map((p) => ({ p, tokens: docTokens(p) }));
  // IDF across the registry, so a word that appears in every entry earns nothing.
  const N = docs.length || 1;
  const df = new Map();
  for (const { tokens } of docs) for (const w of new Set(tokens)) df.set(w, (df.get(w) || 0) + 1);
  const idf = (w) => Math.log(1 + (N - (df.get(w) || 0) + 0.5) / ((df.get(w) || 0) + 0.5));

  const scored = docs.map(({ p, tokens }) => {
    let score = 0;
    const hits = [];
    const freq = new Map();
    for (const w of tokens) freq.set(w, (freq.get(w) || 0) + 1);
    for (const w of q) {
      const tf = freq.get(w) || 0;
      if (tf > 0) { score += (1 + Math.log(tf)) * idf(w); hits.push(w); }
    }
    // Trigger phrases are hand-authored intent markers; count them heavily.
    for (const trig of p.triggers || []) {
      const t = trig.toLowerCase();
      if (t && query.toLowerCase().includes(t)) { score += 4; hits.push(`trigger:${trig}`); }
    }
    for (const w of q) {
      if ((p.category || '').toLowerCase().split(/[^a-z0-9]+/).includes(w)) { score += 1.5; hits.push(`category:${w}`); }
    }
    return { id: p.id, version: p.version, status: p.status, score: p.score, task: p.task,
      category: p.category, provenance: p.provenance, matched: [...new Set(hits)],
      points: Math.round(score * 1000) / 1000 };
  });
  scored.sort((a, b) => b.points - a.points || a.id.localeCompare(b.id));
  return scored.slice(0, top);
}

function writeRouting(registry) {
  const byCat = new Map();
  for (const p of registry.prompts) {
    const c = p.category || p.domain || 'general';
    if (!byCat.has(c)) byCat.set(c, []);
    byCat.get(c).push(p);
  }
  const lines = [
    '# Prompt routing table',
    '',
    '_Generated from `registry.json` by `node tools/route.mjs --write-routing`. Do not hand-edit._',
    '',
    'Registry updated: ' + (registry.updated || 'unknown') + ' | prompts: ' + registry.prompts.length,
    '',
  ];
  for (const c of [...byCat.keys()].sort()) {
    lines.push(`## ${c}`, '');
    for (const p of byCat.get(c).sort((a, b) => a.id.localeCompare(b.id))) {
      lines.push(`- **${p.id}** v${p.version} [${p.status}${p.score === null ? '' : ', score ' + p.score}] - ${p.task}`);
      if (p.triggers && p.triggers.length) lines.push(`  - triggers: ${p.triggers.join(', ')}`);
    }
    lines.push('');
  }
  // ROOT is capabilities/prompts; the skill lives one class over at capabilities/skills.
  const out = path.join(ROOT, '..', 'skills', 'prompt-router', 'references', 'routing.md');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, lines.join('\n') + '\n');
  console.log(`wrote ${out} (${byCat.size} categories, ${registry.prompts.length} prompts)`);
}

const args = process.argv.slice(2);
const registry = readRegistry();

// --selftest: executable gate. Fixture intents with their expected top-1 pick.
// A router whose verification is only "it did not throw" is a dead-button inventory;
// this asserts expected values and exits 1 with the failing fixture named.
if (args.includes('--selftest')) {
  const FIXTURES = [
    ['run the heartbeat and give me the ops report', 'ops-heartbeat-heal-report'],
    ['draft a linkedin post about this but do not publish it', 'linkedin-draft-no-publish'],
    ['audit my job search state and tell me todays moves', 'job-search-state-audit'],
    ['research what is actually working on linkedin growth this year', 'linkedin-growth-2026-research'],
    ['break this heavy summarization job into a chain of prompts', 'pattern-prompt-chain-3step'],
    ['is this agent even alive, just have it echo back', 'probe-connectivity-ack'],
    ['prove this command actually ran, give me raw output', 'probe-exec-raw-stdout'],
    ['review this fix independently, read only', 'independent-read-only-review'],
    // App Studio prompt family (2026-09-28): meta, role, and one stack-fired sub-prompt.
    ['run the app studio mission to build a web app from a video', 'app-studio-meta'],
    ['compose the bench builder prompt for this app task', 'app-studio-builder'],
    ['set up drizzle neon postgres for the app with the pg proxy', 'app-sub-drizzle-neon'],
    // RIG HQ family (2026-09-28): meta, role and interrupt sub-prompt, plus the minor's lane.
    ['operating meta prompt for the office of the ceo', 'rig-hq-meta-office-of-the-ceo'],
    ['revenue meta prompt: offers and pipeline toward the first paying client', 'rig-hq-meta-revenue'],
    ['triage dependency vulnerabilities and sweep for leaked secrets', 'rig-hq-prompt-vera-security'],
    ["draft only content for jacob's recruiting lane", 'rig-hq-prompt-jacob-lane-draft'],
    ['a week passes with no reply on the outreach list', 'rig-hq-sub-j8-2-a-week-passes-with-no-reply'],
  ];
  // RIG HQ body integrity: routing reads registry.json, so a gutted prompt FILE would still
  // rank. Each file must keep a real body and its load-bearing safety phrase.
  const HQ_BODIES = [
    ['rig-hq/meta/office-of-the-ceo.md', /gate-d/i],
    ['rig-hq/meta/revenue.md', /gate-d/i],
    ['rig-hq/prompts/vera-security.md', /redact/i],
    ['rig-hq/prompts/jacob-lane-draft.md', /never auto-run/i],
    ['rig-hq/sub/revenue-week-no-reply.md', /.{40}/],
  ];
  let failed = 0;
  for (const [query, expected] of FIXTURES) {
    const got = rank(query, registry, 1)[0];
    const ok = got && got.id === expected && got.points > 0;
    console.log((ok ? 'PASS' : 'FAIL') + '  "' + query + '" -> ' + (got ? got.id + ' (' + got.points + ')' : 'NOTHING') + (ok ? '' : '  EXPECTED ' + expected));
    if (!ok) failed++;
  }
  for (const [rel, must] of HQ_BODIES) {
    let body = '';
    try { body = parseFrontmatter(fs.readFileSync(path.join(PROMPTS_DIR, rel), 'utf8')).body; } catch (e) { body = ''; }
    const ok = body.trim().length >= 800 && must.test(body);
    console.log((ok ? 'PASS' : 'FAIL') + '  body ' + rel + ' (' + body.trim().length + ' chars, needs >=800 and ' + must + ')');
    if (!ok) failed++;
  }
  const total = FIXTURES.length + HQ_BODIES.length;
  console.log(failed === 0 ? 'SELFTEST PASS: ' + total + '/' + total : 'SELFTEST FAIL: ' + failed + ' of ' + total);
  process.exit(failed === 0 ? 0 : 1);
}

if (args.includes('--write-routing')) {
  writeRouting(registry);
  process.exit(0);
}

const query = args.filter((a) => !a.startsWith('--'))[0];
if (!query) {
  console.error('usage: node tools/route.mjs "<job>" [--json] [--top N] | --write-routing');
  process.exit(2);
}
const topIdx = args.indexOf('--top');
const top = topIdx >= 0 ? Number(args[topIdx + 1]) : 5;
const results = rank(query, registry, top);

if (args.includes('--json')) {
  console.log(JSON.stringify({ query, registry_updated: registry.updated, candidates: results }, null, 2));
} else {
  for (const r of results) {
    console.log(`${String(r.points).padStart(6)}  ${r.id} v${r.version} [${r.status}] ${r.task}`);
    if (r.matched.length) console.log(`        matched: ${r.matched.join(', ')}`);
  }
}
// Exit 0 with an empty-looking top score is a real answer: nothing stored fits.
