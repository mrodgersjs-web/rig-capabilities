import test from 'node:test';
import assert from 'node:assert/strict';
import { chmodSync, mkdtempSync, mkdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const launcher = fileURLToPath(new URL('../scripts/route.mjs', import.meta.url));
const preload = fileURLToPath(new URL('./fixtures/preload.mjs', import.meta.url));
const input = { request: 'Inspect the native launcher', candidates: [{ name: 'functions.exec' }, { name: 'mcp__cua_repl.js' }] };
const expectedReceipt = {
  decision_id: 'fixture-decision',
  status: 'selected',
  decision: { selected: 'functions.exec' },
  input,
  args: ['route', '--stdin'],
};

function fixture(t) {
  const directory = mkdtempSync(join(tmpdir(), 'jevrouter-test-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  return join(directory, 'env');
}

function run(file, variables = {}) {
  const env = { ...process.env };
  for (const name of ['JEV_API_KEY', 'TYPESAFE_API_KEY', 'FIXTURE_KEYCHAIN_KEY', 'FIXTURE_EXPECTED_KEY', 'FIXTURE_EXIT_CODE', 'FIXTURE_FOREIGN_OWNER']) delete env[name];
  const result = spawnSync(process.execPath, ['--import', preload, launcher, 'route', '--stdin'], {
    env: { ...env, S1GATE_ENV_FILE: file, JEV_ROUTER_PROVIDER: 'demo', ...variables },
    input: JSON.stringify(input),
    encoding: 'utf8',
  });
  for (const value of [variables.FIXTURE_EXPECTED_KEY, variables.FIXTURE_KEYCHAIN_KEY].filter(Boolean)) {
    assert.equal(result.stdout.includes(value), false, 'stdout must not disclose credentials');
    assert.equal(result.stderr.includes(value), false, 'stderr must not disclose credentials');
  }
  return result;
}

function selected(result, status = 0) {
  assert.equal(result.status, status);
  assert.deepEqual(JSON.parse(result.stdout), expectedReceipt);
  assert.equal(result.stderr, 'fixture progress\n');
}

test('forwards an inherited Jev key and preserves stdin, stdout, stderr, arguments, provider, and cwd', t => {
  const file = fixture(t);
  selected(run(file, { JEV_API_KEY: 'fixture-jev', TYPESAFE_API_KEY: 'fixture-other', FIXTURE_EXPECTED_KEY: 'fixture-jev' }));
});

test('maps an inherited TypeSafe key to Jev before checking the file', t => {
  selected(run(fixture(t), { TYPESAFE_API_KEY: 'fixture-typesafe', FIXTURE_EXPECTED_KEY: 'fixture-typesafe' }));
});

test('uses native keychain before the env file', t => {
  const file = fixture(t);
  writeFileSync(file, 'TYPESAFE_API_KEY=fixture-file\n', { mode: 0o600 });
  selected(run(file, { FIXTURE_KEYCHAIN_KEY: 'fixture-keychain\n', FIXTURE_EXPECTED_KEY: 'fixture-keychain' }));
});

test('loads only credential assignments from a secure env file without shell evaluation', t => {
  const file = fixture(t);
  const key = 'fixture-$(exit 99)-`exit 98`';
  writeFileSync(file, `OTHER_KEY=ignored\nexport TYPESAFE_API_KEY='${key}'\n`, { mode: 0o600 });
  selected(run(file, { FIXTURE_EXPECTED_KEY: key }));
});

test('prefers Jev when the env file contains both aliases', t => {
  const file = fixture(t);
  writeFileSync(file, 'TYPESAFE_API_KEY=fixture-other\nJEV_API_KEY="fixture-file-jev"\n', { mode: 0o600 });
  selected(run(file, { FIXTURE_EXPECTED_KEY: 'fixture-file-jev' }));
});

test('fails closed for a missing credential with no demo fallback', t => {
  const result = run(fixture(t));
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /No Jev credential available/);
});

test('rejects group or other access on the env file', t => {
  const file = fixture(t);
  writeFileSync(file, 'TYPESAFE_API_KEY=fixture-unsafe\n', { mode: 0o600 });
  chmodSync(file, 0o640);
  const result = run(file);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /Unsafe Jev credential file/);
  assert.equal(result.stderr.includes('fixture-unsafe'), false);
});

test('rejects a symlink to a secure env file', t => {
  const file = fixture(t);
  writeFileSync(`${file}.real`, 'TYPESAFE_API_KEY=fixture-symlink\n', { mode: 0o600 });
  symlinkSync(`${file}.real`, file);
  const result = run(file);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /Unsafe Jev credential file/);
});

test('rejects a regular owner-only file belonging to another uid', t => {
  const file = fixture(t);
  writeFileSync(file, 'TYPESAFE_API_KEY=fixture-foreign\n', { mode: 0o600 });
  const result = run(file, { FIXTURE_FOREIGN_OWNER: '1' });
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /Unsafe Jev credential file/);
});

test('rejects a directory in place of the credential file', t => {
  const file = fixture(t);
  mkdirSync(file, { mode: 0o700 });
  const result = run(file);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /Unsafe Jev credential file/);
});

test('fails closed when a secure file contains no supported credential', t => {
  const file = fixture(t);
  writeFileSync(file, 'OTHER_KEY=fixture-other\n', { mode: 0o600 });
  const result = run(file);
  assert.equal(result.status, 1);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /No Jev credential available/);
});

test('preserves the child exit code', t => {
  selected(run(fixture(t), { JEV_API_KEY: 'fixture-exit', FIXTURE_EXPECTED_KEY: 'fixture-exit', FIXTURE_EXIT_CODE: '2' }), 2);
});
