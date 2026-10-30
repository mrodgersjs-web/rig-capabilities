import childProcess from 'node:child_process';
import fs from 'node:fs';
import { syncBuiltinESMExports } from 'node:module';
import { fileURLToPath } from 'node:url';

const originalSpawn = childProcess.spawnSync;
const fixtureCli = fileURLToPath(new URL('./router-cli.mjs', import.meta.url));
const originalLstat = fs.lstatSync;

fs.lstatSync = (path, ...options) => {
  const stat = originalLstat(path, ...options);
  if (process.env.FIXTURE_FOREIGN_OWNER === '1' && path === process.env.S1GATE_ENV_FILE) stat.uid += 1;
  return stat;
};

childProcess.spawnSync = (command, args, options) => {
  if (command === '/usr/bin/security') {
    return {
      status: process.env.FIXTURE_KEYCHAIN_KEY ? 0 : 44,
      stdout: process.env.FIXTURE_KEYCHAIN_KEY ?? '',
    };
  }
  if (command === process.execPath && args[0] === '/Users/rig128gb/Developer/JevRouter/dist/cli.js') {
    return originalSpawn(command, [fixtureCli, ...args.slice(1)], options);
  }
  throw new Error('Unexpected launcher subprocess');
};
syncBuiltinESMExports();
