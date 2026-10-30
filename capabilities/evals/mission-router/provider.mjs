import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');

export default class MissionRouterProvider {
  id = () => 'rig-mission-router-offline';

  callApi = async (prompt) => {
    const result = spawnSync('python3', [path.join(repo, 'bin/rig-mission'), 'compose',
      String(prompt), '--runtime', 'codex', '--offline', '--repo', repo],
    { cwd: repo, encoding: 'utf8', timeout: 15000, maxBuffer: 4 * 1024 * 1024 });
    if (result.error) return { error: result.error.message };
    if (![0, 2].includes(result.status)) return { error: result.stderr || `exit ${result.status}` };
    try {
      JSON.parse(result.stdout);
    } catch {
      return { error: 'composer returned non-JSON output' };
    }
    return { output: result.stdout };
  };
}
