// promote.mjs — promote a calibrated prompt into the library.
// Usage:
//   node tools/promote.mjs --id <slug> --prompt-file <file.md> \
//     --score <accuracy> --model <name> --task "<desc>" [--domain <d>] \
//     [--history-json <dump/history.json>] [--notes "<text>"]
//
// What it does:
//   1. Copies the prompt into prompts/<id>/versions/v<N>.md (immutable history)
//   2. Rewrites prompts/<id>/prompt.md as the current champion with frontmatter
//   3. Updates registry.json (version, score, model, status: calibrated)
//   4. Appends a hash-chained entry to ledger.jsonl
//   5. If --history-json, copies the score history to prompts/<id>/eval/scores.json
import fs from 'node:fs';
import path from 'node:path';
import {
  ROOT, sha256, readRegistry, writeRegistry, appendLedger,
  promptDir, nextVersion, frontmatter,
} from './lib.mjs';

const args = process.argv.slice(2);
function arg(name) {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : undefined;
}

const id = arg('--id');
const promptFile = arg('--prompt-file');
if (!id || !promptFile) {
  console.error('usage: node tools/promote.mjs --id <slug> --prompt-file <file> --score <n> --model <name> --task "<desc>" [--history-json <file>] [--notes "..."]');
  process.exit(2);
}
const score = arg('--score') ?? null;
const model = arg('--model') ?? 'unknown';
const task = arg('--task') ?? '';
const domain = arg('--domain') ?? 'general';
const notes = arg('--notes') ?? '';
const historyJson = arg('--history-json');

const content = fs.readFileSync(promptFile, 'utf8');
const version = nextVersion(id);
const dir = promptDir(id);
const versionsDir = path.join(dir, 'versions');
fs.mkdirSync(versionsDir, { recursive: true });

// 1. immutable versioned copy
const contentSha = sha256(content);
fs.writeFileSync(path.join(versionsDir, `v${version}.md`), content);

// 2. champion file with frontmatter
const champion = frontmatter({
  id,
  version,
  status: score !== null ? 'calibrated' : 'draft',
  updated: new Date().toISOString().slice(0, 10),
  task,
  domain,
  model_target: model,
  score: score === null ? 'null' : score,
  provenance: notes ? `AutoPrompt calibration (${notes})` : 'AutoPrompt calibration',
  content_sha256: contentSha,
}) + '\n' + content;
fs.writeFileSync(path.join(dir, 'prompt.md'), champion);

// 3. score history
if (historyJson) {
  const evalDir = path.join(dir, 'eval');
  fs.mkdirSync(evalDir, { recursive: true });
  fs.copyFileSync(historyJson, path.join(evalDir, 'scores.json'));
}

// 4. registry
const reg = readRegistry();
const entry = {
  id,
  path: `prompts/${id}/prompt.md`,
  version,
  status: score !== null ? 'calibrated' : 'draft',
  task,
  domain,
  model,
  score: score === null ? null : Number(score),
  added: new Date().toISOString().slice(0, 10),
  provenance: notes || 'AutoPrompt calibration',
};
const existing = reg.prompts.findIndex((p) => p.id === id);
if (existing >= 0) reg.prompts[existing] = { ...reg.prompts[existing], ...entry };
else reg.prompts.push(entry);
writeRegistry(reg);

// 5. ledger
const logged = appendLedger({
  ts: new Date().toISOString(),
  cmd: 'promote',
  id,
  version,
  score: score === null ? null : Number(score),
  model,
  content_sha256: contentSha,
});

console.log(`promoted ${id} v${version} (sha256 ${contentSha.slice(0, 12)}..., score ${score}, ledger hash ${logged.hash.slice(0, 12)}...)`);
