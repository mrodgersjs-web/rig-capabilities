// ingest.mjs — file a DRAFT prompt into the library with honest provenance.
// Companion to promote.mjs: promote files a CALIBRATED winner from an AutoPrompt run;
// ingest files a draft distilled from a session, a command file, or an external source.
// Usage:
//   node tools/ingest.mjs --id <slug> --file <body.md> \
//     --task "<what it gets done>" --category <cat> \
//     --source "<path-or-url>" [--license first-party|MIT|unlicensed] \
//     --triggers "a, b, c" [--compose "when-x/y, projects/z.md"] [--notes "..."]
//
// Honesty contract: a draft always enters with score: null and status: draft. Nothing
// here can mark a prompt calibrated. provenance records where the text actually came
// from; an unlicensed third-party source is recorded as a pattern reference only.
import fs from 'node:fs';
import path from 'node:path';
import {
  sha256, readRegistry, writeRegistry, appendLedger, promptDir, nextVersion, frontmatter,
} from './lib.mjs';

const args = process.argv.slice(2);
function arg(name) { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined; }

const id = arg('--id');
const file = arg('--file');
const task = arg('--task') || '';
const category = arg('--category') || 'general';
const source = arg('--source') || 'unknown';
const license = arg('--license') || 'first-party';
const triggers = (arg('--triggers') || '').split(',').map((s) => s.trim()).filter(Boolean);
const compose = (arg('--compose') || '').split(',').map((s) => s.trim()).filter(Boolean);
const notes = arg('--notes') || '';

if (!id || !file) {
  console.error('usage: node tools/ingest.mjs --id <slug> --file <body.md> --task "<task>" --category <cat> --source "<src>" [--license L] --triggers "a, b" [--compose "x, y"] [--notes "..."]');
  process.exit(2);
}
if (!/^[a-z0-9][a-z0-9-]*$/.test(id)) {
  console.error(`refused: id "${id}" must be a lowercase slug`);
  process.exit(2);
}
if (!fs.existsSync(file)) {
  console.error(`refused: ${file} does not exist`);
  process.exit(2);
}

const body = fs.readFileSync(file, 'utf8').trim() + '\n';
const contentSha = sha256(body);
const dir = promptDir(id);
const versionsDir = path.join(dir, 'versions');
fs.mkdirSync(versionsDir, { recursive: true });
const version = nextVersion(id);

// 1. immutable versioned copy
fs.writeFileSync(path.join(versionsDir, `v${version}.md`), body);

// 2. champion with frontmatter (draft; score stays null)
const provenance = notes ? `${source} | ${notes}` : source;
const champion = frontmatter({
  id,
  version,
  status: 'draft',
  updated: new Date().toISOString().slice(0, 10),
  task,
  category,
  domain: category,
  model_target: 'unspecified',
  score: 'null',
  license,
  source,
  triggers: triggers.join(' '),
  compose: compose.join(' '),
  provenance,
  content_sha256: contentSha,
}) + '\n' + body;
fs.writeFileSync(path.join(dir, 'prompt.md'), champion);

// 3. registry
const reg = readRegistry();
const entry = {
  id,
  path: `prompts/${id}/prompt.md`,
  version,
  status: 'draft',
  task,
  category,
  domain: category,
  model: 'unspecified',
  score: null,
  license,
  source,
  triggers,
  compose,
  added: new Date().toISOString().slice(0, 10),
  provenance,
};
const existing = reg.prompts.findIndex((p) => p.id === id);
if (existing >= 0) reg.prompts[existing] = { ...reg.prompts[existing], ...entry };
else reg.prompts.push(entry);
writeRegistry(reg);

// 4. ledger (hash-chained)
const logged = appendLedger({
  ts: new Date().toISOString(),
  cmd: 'ingest',
  id,
  version,
  score: null,
  content_sha256: contentSha,
  source,
  license,
});

console.log(`ingested ${id} v${version} (draft, sha256 ${contentSha.slice(0, 12)}..., ledger ${logged.hash.slice(0, 12)}...)`);
