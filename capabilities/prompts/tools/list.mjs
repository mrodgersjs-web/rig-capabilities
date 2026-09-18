// list.mjs — print the registry as a table.
// Usage: node tools/list.mjs [--domain <d>] [--status <s>]
import { readRegistry } from './lib.mjs';

const args = process.argv.slice(2);
const domainI = args.indexOf('--domain');
const statusI = args.indexOf('--status');
let rows = readRegistry().prompts;
if (domainI >= 0) rows = rows.filter((r) => r.domain === args[domainI + 1]);
if (statusI >= 0) rows = rows.filter((r) => r.status === args[statusI + 1]);

console.log('ID'.padEnd(28), 'v'.padEnd(4), 'STATUS'.padEnd(11), 'SCORE'.padEnd(8), 'MODEL'.padEnd(12), 'TASK');
for (const r of rows) {
  console.log(
    r.id.padEnd(28),
    String(r.version).padEnd(4),
    r.status.padEnd(11),
    (r.score === null || r.score === undefined ? '-' : r.score).toString().padEnd(8),
    (r.model ?? '-').padEnd(12),
    (r.task ?? '').slice(0, 60),
  );
}
console.log(`\n${rows.length} prompt(s)`);
