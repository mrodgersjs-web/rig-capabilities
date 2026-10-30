import { readFileSync } from 'node:fs';

const key = process.env.FIXTURE_EXPECTED_KEY;
if (!key || process.env.JEV_API_KEY !== key || process.env.TYPESAFE_API_KEY !== key) {
  process.stderr.write('Fixture credential forwarding failed\n');
  process.exit(91);
}
if (process.env.JEV_ROUTER_PROVIDER !== 'typesafe' || process.cwd() !== '/Users/rig128gb/Developer/JevRouter') {
  process.stderr.write('Fixture provider or working directory failed\n');
  process.exit(92);
}
process.stdout.write(JSON.stringify({
  decision_id: 'fixture-decision',
  status: 'selected',
  decision: { selected: 'functions.exec' },
  input: JSON.parse(readFileSync(0, 'utf8')),
  args: process.argv.slice(2),
}));
process.stderr.write('fixture progress\n');
process.exit(Number(process.env.FIXTURE_EXIT_CODE ?? 0));
