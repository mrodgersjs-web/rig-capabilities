#!/usr/bin/env node
// Stitch generation driver for the night-lane design-studio app.
// Speaks MCP JSON-RPC over stdio to /Users/rig128gb/.rig/bin/stitch-mcp proxy
// (keychain-backed Stitch proxy — no browser automation), generates the three
// screens in ../.stitch/prompts/, downloads HTML + screenshots into
// ../.stitch/designs/, and writes manifest.json (STITCH-OK / STITCH-PARTIAL /
// STITCH-BLOCKED with the exact error). Never fabricates screenshots: a screen
// with no downloaded image is reported as such and the UI renders its internal
// mock preview instead.

import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const STITCH_DIR = path.resolve(HERE, '..', '.stitch');
const DESIGNS = path.join(STITCH_DIR, 'designs');
const PROMPTS = path.join(STITCH_DIR, 'prompts');
const BIN = '/Users/rig128gb/.rig/bin/stitch-mcp';

const SCREENS = [
  {
    slug: 'canvas-board-view',
    title: 'Canvas board view',
    description:
      'Infinite pan/zoom design canvas with artifact cards, connection lines, marquee select, and the design-system side panel.',
    prompt: 'screen-1-canvas-board-view.md',
  },
  {
    slug: 'double-diamond-stage-view',
    title: 'Double Diamond stage view',
    description: 'Discover → Define → Develop → Deliver rails with stage artifacts and phase headers.',
    prompt: 'screen-2-double-diamond-stage-view.md',
  },
  {
    slug: 'design-system-panel',
    title: 'Design system panel',
    description:
      'Token table from MASTER-CREATIVE-PROMPT v3.0, live apply-tokens toggle, and the AI-coding prompt composer.',
    prompt: 'screen-3-design-system-panel.md',
  },
  // ── round 2 (2026-09-30) ─────────────────────────────────────────────────
  {
    slug: 'export-handoff-modal',
    title: 'Export handoff modal',
    description:
      'Board → coding agent: serializer counts, rig-dev-handoff.json + rig-ai-coding-prompts.md rows, JSON preview, download both.',
    prompt: 'screen-4-export-handoff-modal.md',
    device: 'DESKTOP',
    r2: true,
  },
  {
    slug: 'mobile-canvas-view',
    title: 'Mobile canvas view (390px)',
    description:
      'The canvas adapted to a 390px phone viewport: segmented tabs, full-width artifact cards, bottom action bar.',
    prompt: 'screen-5-mobile-canvas-view.md',
    device: 'MOBILE',
    r2: true,
  },
];

class McpClient {
  constructor() {
    this.nextId = 1;
    this.pending = new Map();
    this.buf = '';
    this.child = spawn(BIN, ['proxy'], { stdio: ['pipe', 'pipe', 'pipe'] });
    this.child.stdout.setEncoding('utf8');
    this.child.stdout.on('data', (chunk) => {
      this.buf += chunk;
      let idx;
      while ((idx = this.buf.indexOf('\n')) >= 0) {
        const line = this.buf.slice(0, idx).trim();
        this.buf = this.buf.slice(idx + 1);
        if (!line) continue;
        let msg;
        try {
          msg = JSON.parse(line);
        } catch {
          continue;
        }
        if (msg.id !== undefined && this.pending.has(msg.id)) {
          const { resolve, reject, timer } = this.pending.get(msg.id);
          clearTimeout(timer);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(JSON.stringify(msg.error)));
          else resolve(msg.result);
        }
      }
    });
    this.child.stderr.setEncoding('utf8');
    this.stderrLog = '';
    this.child.stderr.on('data', (c) => {
      this.stderrLog += c;
    });
    this.child.on('exit', (code) => {
      for (const [id, { reject, timer }] of this.pending) {
        clearTimeout(timer);
        reject(new Error(`stitch-mcp exited (code ${code}) mid-request ${id}; stderr: ${this.stderrLog.slice(-500)}`));
      }
      this.pending.clear();
    });
  }

  request(method, params, timeoutMs = 300_000) {
    const id = this.nextId++;
    const payload = JSON.stringify({ jsonrpc: '2.0', id, method, params });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`timeout after ${timeoutMs}ms waiting for ${method}`));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.child.stdin.write(payload + '\n');
    });
  }

  notify(method, params) {
    this.child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
  }

  close() {
    this.child.stdin.end();
  }
}

function findTool(tools, ...needles) {
  return tools.find((t) => needles.some((n) => t.name.toLowerCase().includes(n)));
}

// Stitch tool responses wrap JSON in content[0].text (and may duplicate it under
// structuredContent) with outputComponents[].design.screens[].screenshot/htmlCode
// .downloadUrl — signed URLs with no file extension. Parse that structure; fall
// back to any downloadUrl fields.
function extractAssets(result) {
  let inner = result;
  try {
    const text = result?.content?.find((c) => c.type === 'text')?.text;
    if (text) inner = JSON.parse(text);
  } catch {
    inner = result;
  }
  const comps = inner?.outputComponents ?? [];
  for (const comp of comps) {
    const screens = comp?.design?.screens ?? comp?.screens ?? [];
    for (const sc of screens) {
      const imgUrl = sc?.screenshot?.downloadUrl;
      const htmlUrl = sc?.htmlCode?.downloadUrl;
      if (imgUrl || htmlUrl) return { imgUrl, htmlUrl, screenName: sc?.name ?? null };
    }
  }
  const flat = [];
  const walk = (v) => {
    if (v && typeof v === 'object') {
      if (typeof v.downloadUrl === 'string') flat.push(v.downloadUrl);
      for (const x of Array.isArray(v) ? v : Object.values(v)) walk(x);
    }
  };
  walk(inner);
  return {
    imgUrl: flat.find((u) => /googleusercontent|image|screenshot|lh3/i.test(u)) ?? flat[0],
    htmlUrl: flat.find((u) => /html|contribution|download\?c=/i.test(u)) ?? flat[1],
    screenName: null,
  };
}

async function download(url, dest) {
  let res = await fetch(url, { redirect: 'follow' });
  if (!res.ok && process.env.STITCH_API_KEY) {
    res = await fetch(url, { redirect: 'follow', headers: { 'X-Goog-Api-Key': process.env.STITCH_API_KEY } });
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  const type = res.headers.get('content-type') ?? '';
  const buf = Buffer.from(await res.arrayBuffer());
  if (buf.length < 100) throw new Error(`suspiciously small (${buf.length}B) download from ${url}`);
  await writeFile(dest, buf);
  return type;
}

// Manifest is merged with the previous state: a screen that fails in this run
// keeps its old entry (image/html) instead of being wiped. Round-2 failures are
// reported as STITCH-R2-BLOCKED with the exact error while old entries survive.
async function writeManifest(status, extra) {
  const prevScreens = extra.prev?.screens ?? [];
  const screens = SCREENS.map((s) => {
    const before = prevScreens.find((p) => p.slug === s.slug) ?? {};
    const img = extra.images[s.slug] ?? (before.image && existsSync(path.join(DESIGNS, before.image)) ? before.image : '');
    const html = extra.htmls[s.slug] ?? (before.html && existsSync(path.join(DESIGNS, before.html)) ? before.html : '');
    return {
      slug: s.slug,
      title: s.title,
      description: s.description,
      image: img,
      html: html,
      stitchScreenId: extra.screenIds[s.slug] ?? before.stitchScreenId ?? null,
    };
  });
  await writeFile(
    path.join(DESIGNS, 'manifest.json'),
    JSON.stringify(
      {
        status,
        projectTitle: 'RIG Design Studio — Stitch mockups',
        projectId: extra.projectId ?? extra.prev?.projectId ?? null,
        generatedAt: new Date().toISOString(),
        error: extra.error ?? null,
        screens,
      },
      null,
      2,
    ),
  );
  return screens;
}

async function main() {
  await mkdir(DESIGNS, { recursive: true });
  const images = {};
  const htmls = {};
  const screenIds = {};
  const prompts = {};
  const errors = {};
  let prev = null;
  try {
    prev = JSON.parse(await readFile(path.join(DESIGNS, 'manifest.json'), 'utf8'));
  } catch {
    /* no previous manifest */
  }
  for (const s of SCREENS) prompts[s.slug] = await readFile(path.join(PROMPTS, s.prompt), 'utf8');

  const client = new McpClient();
  try {
    const init = await client.request(
      'initialize',
      {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: { name: 'rig-design-studio-night', version: '0.1.0' },
      },
      60_000,
    );
    client.notify('notifications/initialized', {});
    console.log(`[stitch-run] connected: ${JSON.stringify(init.serverInfo ?? init)}`);

    const toolsResult = await client.request('tools/list', {}, 60_000);
    const tools = toolsResult.tools ?? [];
    console.log(`[stitch-run] tools: ${tools.map((t) => t.name).join(', ')}`);

    const genTool = findTool(tools, 'generate_screen');
    const listTool = findTool(tools, 'list_projects');
    const createTool = findTool(tools, 'create_project');
    if (!genTool) throw new Error(`no generate_screen tool on stitch-mcp; got: ${tools.map((t) => t.name).join(', ')}`);

    // Resolve project: reuse "RIG Design Studio — Night Lane" if present, else create.
    let projectId;
    if (listTool) {
      const listed = await client.request('tools/call', { name: listTool.name, arguments: {} }, 120_000);
      const text = JSON.stringify(listed);
      const m = text.match(/projects\/(\d+)/) ?? text.match(/"id"\s*:\s*"?(\d{10,})/);
      if (m) projectId = m[1];
    }
    if (!projectId && createTool) {
      const created = await client.request(
        'tools/call',
        { name: createTool.name, arguments: { title: 'RIG Design Studio — Night Lane' } },
        120_000,
      );
      const m = JSON.stringify(created).match(/projects\/(\d+)/) ?? JSON.stringify(created).match(/"id"\s*:\s*"?(\d{10,})/);
      if (m) projectId = m[1];
    }
    if (!projectId) throw new Error(`could not resolve or create a Stitch project; list/create raw: no id matched`);
    console.log(`[stitch-run] project ${projectId}`);

    for (const s of SCREENS) {
      const rawPath = path.join(DESIGNS, `raw-${s.slug}.json`);
      const reused = !process.argv.includes('--regen') && existsSync(rawPath);
      try {
        let result;
        if (reused) {
          console.log(`[stitch-run] reusing existing response for ${s.slug}`);
          result = JSON.parse(await readFile(rawPath, 'utf8'));
        } else {
          console.log(`[stitch-run] generating ${s.slug} (${s.device ?? 'DESKTOP'}) …`);
          result = await client.request(
            'tools/call',
            {
              name: genTool.name,
              arguments: { projectId, prompt: prompts[s.slug], deviceType: s.device ?? 'DESKTOP' },
            },
            300_000,
          );
          await writeFile(rawPath, JSON.stringify(result, null, 2));
        }
        const sid = JSON.stringify(result).match(/screens\/([a-f0-9]{16,})/);
        if (sid) screenIds[s.slug] = sid[1];
        const { imgUrl, htmlUrl } = extractAssets(result);
        const haveImg = existsSync(path.join(DESIGNS, `${s.slug}.png`));
        const haveHtml = existsSync(path.join(DESIGNS, `${s.slug}.html`));
        if (imgUrl && !(reused && haveImg)) {
          await download(imgUrl, path.join(DESIGNS, `${s.slug}.png`));
          console.log(`[stitch-run] saved ${s.slug}.png`);
        } else if (haveImg) {
          console.log(`[stitch-run] kept existing ${s.slug}.png`);
        }
        if (imgUrl || haveImg) images[s.slug] = `${s.slug}.png`;
        if (htmlUrl && !(reused && haveHtml)) {
          await download(htmlUrl, path.join(DESIGNS, `${s.slug}.html`));
          console.log(`[stitch-run] saved ${s.slug}.html`);
        } else if (haveHtml) {
          console.log(`[stitch-run] kept existing ${s.slug}.html`);
        }
        if (htmlUrl || haveHtml) htmls[s.slug] = `${s.slug}.html`;
        if (!imgUrl && !htmlUrl && !haveImg && !haveHtml) {
          throw new Error(`no asset urls in response for ${s.slug}; see raw-${s.slug}.json`);
        }
      } catch (err) {
        errors[s.slug] = err.message;
        console.error(`[stitch-run] ${s.slug} failed: ${err.message}`);
      }
    }

    const assetPresent = (s) =>
      Boolean(images[s.slug] || htmls[s.slug]) ||
      Boolean((prev?.screens ?? []).find((p) => p.slug === s.slug && p.image && existsSync(path.join(DESIGNS, p.image))));
    const got = SCREENS.filter(assetPresent).length;
    const allErrors = Object.entries(errors)
      .map(([k, v]) => `${k}: ${v}`)
      .join(' | ');
    const failedR2 = SCREENS.filter((s) => s.r2 && errors[s.slug]);
    let status;
    let error = null;
    if (failedR2.length) {
      // Round-2 generation failure: old manifest state is preserved (merge in
      // writeManifest), and the exact error is surfaced.
      status = 'STITCH-R2-BLOCKED';
      error = failedR2.map((s) => `${s.slug}: ${errors[s.slug]}`).join(' | ');
    } else if (got === SCREENS.length) {
      status = 'STITCH-OK';
      error = allErrors || null;
    } else if (got > 0) {
      status = 'STITCH-PARTIAL';
      error = `screens with downloaded screenshots: ${got}/${SCREENS.length}${allErrors ? `; ${allErrors}` : ''}; see raw-*.json`;
    } else {
      status = 'STITCH-BLOCKED';
      error = allErrors || 'no screenshots downloaded; see raw-*.json';
    }
    await writeManifest(status, { images, htmls, screenIds, projectId, error, prev });
    console.log(`[stitch-run] manifest written: ${status}`);
  } catch (err) {
    console.error(`[stitch-run] BLOCKED: ${err.message}`);
    await writeManifest(prev ? 'STITCH-R2-BLOCKED' : 'STITCH-BLOCKED', {
      images,
      htmls,
      screenIds,
      error: err.message,
      prev,
    });
    process.exitCode = 2;
  } finally {
    client.close();
  }
}

main();
