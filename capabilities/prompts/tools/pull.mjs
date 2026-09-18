// pull.mjs — print a library prompt to stdout (for pasting into any app/agent).
// Usage: node tools/pull.mjs <id> [--version N] [--body]
//   --version N : print an archived version instead of the champion
//   --body      : strip frontmatter, print prompt text only
import fs from 'node:fs';
import path from 'node:path';
import { readRegistry, appendLedger, promptDir, parseFrontmatter, sha256 } from './lib.mjs';

const args = process.argv.slice(2);
const id = args.find((a) => !a.startsWith('--'));
if (!id) {
  console.error('usage: node tools/pull.mjs <id> [--version N] [--body]');
  process.exit(2);
}
const reg = readRegistry();
if (!reg.prompts.some((p) => p.id === id)) {
  console.error(`BLOCKED: id "${id}" not in registry.json`);
  process.exit(1);
}
const vi = args.indexOf('--version');
const file = vi >= 0
  ? path.join(promptDir(id), 'versions', `v${args[vi + 1]}.md`)
  : path.join(promptDir(id), 'prompt.md');
if (!fs.existsSync(file)) {
  console.error(`BLOCKED: ${file} missing`);
  process.exit(1);
}
const text = fs.readFileSync(file, 'utf8');

appendLedger({
  ts: new Date().toISOString(),
  cmd: 'pull',
  id,
  version: vi >= 0 ? Number(args[vi + 1]) : undefined,
  content_sha256: parseFrontmatter(text).meta.content_sha256 ?? sha256(text),
});
const out = args.includes('--body') ? parseFrontmatter(text).body : text;
process.stdout.write(out);
