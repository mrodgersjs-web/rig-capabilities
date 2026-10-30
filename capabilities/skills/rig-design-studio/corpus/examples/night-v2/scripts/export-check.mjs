#!/usr/bin/env node
// Export loop check: runs the dev-handoff serializer on seed.ts and asserts the
// JSON export counts match the seed board (cards, per-phase, links) end to end.
// Tiny on purpose — no test framework. Exit 0 = pass, 1 = fail.

import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP = path.resolve(HERE, '..');
const OUT = mkdtempSync(path.join(tmpdir(), 'export-check-'));

const failures = [];
function check(label, actual, expected) {
  const ok = JSON.stringify(actual) === JSON.stringify(expected);
  if (!ok) failures.push(`${label}: got ${JSON.stringify(actual)}, expected ${JSON.stringify(expected)}`);
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${label} = ${JSON.stringify(actual)}`);
}

// 1. Compile the serializer chain (types/seed/store/tokens/export) to CJS so node can run TS sources.
console.log('[export-check] compiling src/{types,seed,store,tokens,export}.ts →', OUT);
execFileSync(
  path.join(APP, 'node_modules/.bin/tsc'),
  ['src/types.ts', 'src/seed.ts', 'src/store.ts', 'src/tokens.ts', 'src/export.ts',
   '--module', 'commonjs', '--target', 'es2020', '--moduleResolution', 'node',
   '--skipLibCheck', '--outDir', OUT],
  { cwd: APP, stdio: 'inherit' },
);

const require = createRequire(path.join(APP, 'x.js'));
const { serializeBoard, promptBundle } = require(path.join(OUT, 'export.js'));
const { seedBoard } = require(path.join(OUT, 'seed.js'));

const seed = seedBoard();
const exp = serializeBoard(seed, '2026-09-30T00:00:00.000Z');
console.log(`[export-check] board: "${seed.title}"`);

// 2. Counts must match the seed source.
console.log('[export-check] counts');
const phaseCounts = Object.fromEntries(
  ['discover', 'define', 'develop', 'deliver'].map((p) => [p, seed.cards.filter((c) => c.phase === p).length]),
);
check('cards', exp.counts.cards, seed.cards.length);
check('links', exp.counts.links, seed.links.length);
check('phases', exp.counts.phases, phaseCounts);
check('serialized card rows', exp.cards.length, seed.cards.length);

// 3. Structure invariants the serializer could silently break.
console.log('[export-check] invariants');
const ids = new Set(seed.cards.map((c) => c.id));
check('unique card ids', ids.size, seed.cards.length);
check('unique link ids', new Set(seed.links.map((l) => l.id)).size, seed.links.length);
check('all link endpoints resolve', seed.links.every((l) => ids.has(l.from) && ids.has(l.to)), true);
check('every card has deviation + phase', exp.cards.every((c) => typeof c.deviation === 'number' && c.phaseLabel), true);
check('every card has token set bound', exp.tokenSet.colors.length > 0 && exp.tokenSet.name, 'MASTER-CREATIVE-PROMPT v3.0');
check('min 4 artifacts per phase', Object.values(exp.counts.phases).every((n) => n >= 4), true);

// 4. Prompt bundle: board-level prompt + one per-card prompt.
console.log('[export-check] prompt bundle');
const md = promptBundle(seed);
check('board-level prompt present', md.includes('RIG AI-CODING PROMPT BUNDLE'), true);
check('per-card prompts', (md.match(/^# RIG AI-CODING PROMPT — /gm) ?? []).length, seed.cards.length);
check('bundle covers every phase', ['Discover', 'Define', 'Develop', 'Deliver'].every((p) => md.includes(p)), true);

if (failures.length) {
  console.error(`\n[export-check] FAIL — ${failures.length} assertion(s):`);
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('\n[export-check] PASS — serializer output matches seed.ts on cards, phases, links.');
