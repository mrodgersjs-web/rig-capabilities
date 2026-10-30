import { spawnSync } from 'node:child_process';
import { closeSync, constants, fstatSync, lstatSync, openSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

function readCredentialFile(path) {
  let descriptor;
  try {
    const before = lstatSync(path);
    if (!before.isFile() || before.uid !== process.getuid() || (before.mode & 0o077)) {
      throw new Error('Unsafe Jev credential file');
    }
    descriptor = openSync(path, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
    const opened = fstatSync(descriptor);
    if (!opened.isFile() || opened.uid !== process.getuid() || (opened.mode & 0o077)
      || opened.ino !== before.ino || opened.dev !== before.dev) {
      throw new Error('Unsafe Jev credential file');
    }
    const credentials = {};
    for (const line of readFileSync(descriptor, 'utf8').split(/\r?\n/)) {
      const match = line.match(/^\s*(?:export\s+)?(JEV_API_KEY|TYPESAFE_API_KEY)\s*=\s*(.*?)\s*$/);
      if (!match) continue;
      let value = match[2];
      if (value.startsWith('"') || value.startsWith("'")) {
        const quoted = value.match(/^(['"])(.*?)\1(?:\s+#.*)?$/);
        if (!quoted) throw new Error('Invalid Jev credential assignment');
        value = quoted[2];
      } else {
        value = value.replace(/\s+#.*$/, '').trim();
      }
      if (value.includes('\0')) throw new Error('Invalid Jev credential assignment');
      credentials[match[1]] = value.trim();
    }
    return credentials.JEV_API_KEY || credentials.TYPESAFE_API_KEY;
  } catch (error) {
    if (error.code === 'ENOENT') return undefined;
    if (error.message === 'Invalid Jev credential assignment') throw error;
    throw new Error('Unsafe Jev credential file');
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

try {
  let key = process.env.JEV_API_KEY?.trim() || process.env.TYPESAFE_API_KEY?.trim();
  if (!key) {
    const result = spawnSync('/usr/bin/security', ['find-generic-password', '-s', 'com.rig.env.TYPESAFE_API_KEY', '-w'], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 5000,
    });
    if (result.status === 0 && !result.error) key = result.stdout?.trim();
  }
  key ||= readCredentialFile(process.env.S1GATE_ENV_FILE || join(homedir(), '.rig/s1gate/env'));
  if (!key) throw new Error('No Jev credential available');

  const result = spawnSync(process.execPath, ['/Users/rig128gb/Developer/JevRouter/dist/cli.js', ...process.argv.slice(2)], {
    cwd: '/Users/rig128gb/Developer/JevRouter',
    env: { ...process.env, JEV_API_KEY: key, TYPESAFE_API_KEY: key, JEV_ROUTER_PROVIDER: 'typesafe' },
    stdio: 'inherit',
  });
  if (result.error) console.error('JevRouter launcher failed to start the native CLI');
  process.exit(result.status ?? 1);
} catch (error) {
  console.error('JevRouter launcher failed: ' + error.message);
  process.exit(1);
}
