import { Database } from "bun:sqlite";
import { describe, expect, test } from "bun:test";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";


import {
  buildTurnState,
  classifyAnswers,
  redactSecrets,
  registerExtension,
  reserveGlobalQuota,
  settleGlobalQuota,
  verifyStateLive,
  type VerificationAnswers,
} from "../src/extension";

const safeAnswers: VerificationAnswers = {
  unsupported_factual_claim: 0.04,
  contradicts_evidence: 0.02,
  overstates_completion: 0.03,
  fabricated_citation_or_path: 0.01,
  uncertainty_presented_as_fact: 0.05,
};

function message(role: string, text: string, toolName?: string) {
  return {
    type: "message",
    message: {
      role,
      ...(toolName ? { toolName } : {}),
      content: [{ type: "text", text }],
    },
  };
}

function asRecord(value: unknown): Record<string, unknown> {
  expect(value).toBeObject();
  return value as Record<string, unknown>;
}

function quotaOptions(stateRoot: string) {
  return {
    stateRoot,
    dailyBudgetUsd: 0.10,
    dailyMaxCalls: 100,
    inputPricePerMillionUsd: 0.042,
  };
}

describe("TypeSafe verifier domain", () => {
  test("redacts common API, cloud, chat, URL, and private-key credentials", () => {
    const input = [
      "Authorization: Bearer secret-token",
      "TYPESAFE_API_KEY=apikey_abc123",
      'TYPESAFE_API_KEY="quoted-env-secret"',
      '{"password":"json-password","access_token":"json-access","refresh_token":"json-refresh"}',
      "sk-live-xyz",
      "AKIAIOSFODNN7EXAMPLE",
      "ghp_abcdefghijklmnopqrstuvwxyz123456",
      "xoxb-123456789-abcdefgh",
      "ya29.a0AfH6SMExample",
      "https://alice:supersecret@example.com/path",
      "-----BEGIN PRIVATE KEY----- secret -----END PRIVATE KEY-----",
    ].join("\n");
    const output = redactSecrets(input);
    for (const secret of [
      "secret-token",
      "apikey_abc123",
      "quoted-env-secret",
      "json-password",
      "json-access",
      "json-refresh",
      "sk-live-xyz",
      "AKIAIOSFODNN7EXAMPLE",
      "ghp_abcdefghijklmnopqrstuvwxyz123456",
      "xoxb-123456789-abcdefgh",
      "ya29.a0AfH6SMExample",
      "supersecret",
      "BEGIN PRIVATE KEY",
    ]) {
      if (output.includes(secret)) throw new Error(`secret was not redacted: ${secret}`);
    }
    expect(output).toContain("[REDACTED]");
  });

  test("builds bounded state from only the latest turn", () => {
    const state = buildTurnState([
      message("user", "old request apikey_old"),
      message("assistant", "old answer"),
      message("user", "Fix the retry contract."),
      message("toolResult", "retry test passed", "bash"),
      message("assistant", "Retry handling is fixed and the retry test passed."),
    ]);
    expect(state?.request).toBe("Fix the retry contract.");
    expect(state?.response).toBe("Retry handling is fixed and the retry test passed.");
    expect(state?.evidence).toEqual([{ tool: "bash", text: "retry test passed" }]);
    expect(JSON.stringify(state)).not.toContain("apikey_old");
  });
  test("builds evidence enriched with tool call input details", () => {
    const state = buildTurnState([
      message("user", "Commit the reports"),
      {
        type: "message",
        message: {
          role: "assistant",
          content: [
            {
              type: "toolCall",
              id: "call_git",
              name: "bash",
              arguments: { command: "git commit -m 'test'" },
            },
          ],
        },
      },
      {
        type: "message",
        message: {
          role: "toolResult",
          toolCallId: "call_git",
          toolName: "bash",
          content: [{ type: "text", text: "ok 123456" }],
        },
      },
      message("assistant", "Committed test report"),
    ]);
    expect(state?.evidence).toEqual([
      { tool: "bash", text: "Input: command: git commit -m 'test'\nOutput:\nok 123456" },
    ]);
  });

  test("safe evidence-backed answers pass", () => {
    expect(classifyAnswers(safeAnswers)).toEqual({ verdict: "pass", maxRisk: 0.05, trigger: "uncertainty_presented_as_fact" });
  });

  test("unsupported claim forces review", () => {
    expect(classifyAnswers({ ...safeAnswers, unsupported_factual_claim: 0.92 })).toEqual({
      verdict: "review",
      maxRisk: 0.92,
      trigger: "unsupported_factual_claim",
    });
  });

  test("missing answer is unavailable", () => {
    const incomplete = { ...safeAnswers } as Partial<VerificationAnswers>;
    delete incomplete.contradicts_evidence;
    expect(classifyAnswers(incomplete)).toEqual({ verdict: "unavailable", maxRisk: 1, trigger: "missing_or_invalid_answer" });
  });

  test("global quota persists across process reservations and caps cost", () => {
    const state = { request: "request", response: "response", evidence: [] };
    const root = mkdtempSync(join(tmpdir(), "typesafe-quota-"));
    const now = new Date("2026-09-16T21:00:00Z");
    try {
      const options = {
        stateRoot: root,
        dailyBudgetUsd: 0.10,
        dailyMaxCalls: 1,
        inputPricePerMillionUsd: 0.042,
      };
      expect(reserveGlobalQuota(state, options, now)).toMatchObject({
        allowed: true,
        callIndex: 1,
        dailyMaxCalls: 1,
        estimatedCallCostUsd: 0.001344,
        reservedCostUsd: 0.001344,
      });
      expect(reserveGlobalQuota(state, options, now)).toMatchObject({
        allowed: false,
        reason: "daily_call_limit",
        callIndex: 1,
      });

      const budgetRoot = join(root, "zero-budget");
      expect(reserveGlobalQuota(state, { ...options, stateRoot: budgetRoot, dailyMaxCalls: 100, dailyBudgetUsd: 0 }, now)).toMatchObject({
        allowed: false,
        reason: "daily_cost_limit",
      });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("settlement refunds the unused part of a reservation and never raises spend", () => {
    const state = { request: "request", response: "response", evidence: [] };
    const root = mkdtempSync(join(tmpdir(), "typesafe-settle-"));
    const now = new Date("2026-09-20T21:00:00Z");
    const options = {
      stateRoot: root,
      dailyBudgetUsd: 0.10,
      dailyMaxCalls: 100,
      inputPricePerMillionUsd: 0.042,
    };
    const ledger = () => JSON.parse(readFileSync(join(root, "quota.json"), "utf8"));
    try {
      // A 2k-token check reserves the 32k ceiling ($0.001344) up front...
      const reservation = reserveGlobalQuota(state, options, now);
      expect(reservation).toMatchObject({ allowed: true, reservedCostUsd: 0.001344 });

      // ...and settlement hands back the 30k tokens it never used.
      expect(settleGlobalQuota(reservation, 2_000, options, now)).toMatchObject({
        settled: true,
        reason: "settled",
        actualCallCostUsd: 0.000084,
        refundedUsd: 0.00126,
        reservedCostUsd: 0.000084,
      });
      expect(ledger()).toMatchObject({ calls: 1, reserved_cost_usd: 0.000084 });

      // Usage at or above the ceiling refunds nothing: the worst case stands.
      const atCeiling = reserveGlobalQuota(state, options, now);
      expect(settleGlobalQuota(atCeiling, 99_000, options, now)).toMatchObject({
        settled: false,
        reason: "settled",
        refundedUsd: 0,
      });
      expect(ledger()).toMatchObject({ calls: 2, reserved_cost_usd: 0.001428 });

      // A response with no usage block keeps the full reservation.
      const noUsage = reserveGlobalQuota(state, options, now);
      expect(settleGlobalQuota(noUsage, undefined, options, now)).toMatchObject({
        settled: false,
        reason: "no_usage",
      });
      expect(ledger()).toMatchObject({ calls: 3, reserved_cost_usd: 0.002772 });

      // A refused reservation can never be used to mint a refund.
      const refused = reserveGlobalQuota(state, { ...options, dailyBudgetUsd: 0 }, now);
      expect(refused.allowed).toBe(false);
      expect(settleGlobalQuota(refused, 1, options, now)).toMatchObject({
        settled: false,
        reason: "not_reserved",
      });
      expect(ledger()).toMatchObject({ calls: 3, reserved_cost_usd: 0.002772 });

      // A day boundary crossed mid-call must not refund into the new ledger.
      const rolled = reserveGlobalQuota(state, options, new Date("2026-09-21T00:30:00Z"));
      expect(settleGlobalQuota({ ...rolled, day: "2026-09-20" }, 1_000, options, now)).toMatchObject({
        settled: false,
        reason: "day_rolled",
      });
      expect(ledger()).toMatchObject({ day: "2026-09-21", reserved_cost_usd: 0.001344 });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("malformed and locked quota state fail closed", () => {
    const state = { request: "request", response: "response", evidence: [] };
    const root = mkdtempSync(join(tmpdir(), "typesafe-quota-invalid-"));
    try {
      writeFileSync(join(root, "quota.json"), "{}\\n", "utf8");
      const options = {
        stateRoot: root,
        dailyBudgetUsd: 0.10,
        dailyMaxCalls: 100,
        inputPricePerMillionUsd: 0.042,
      };
      expect(reserveGlobalQuota(state, options)).toMatchObject({
        allowed: false,
        reason: "quota_state_invalid",
      });
      rmSync(join(root, "quota.json"));
      writeFileSync(join(root, "quota.lock"), "other-owner", "utf8");
      expect(reserveGlobalQuota(state, options)).toMatchObject({
        allowed: false,
        reason: "quota_lock_busy",
      });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("reclaims only stale locks whose recorded owner is dead", async () => {
    const root = mkdtempSync(join(tmpdir(), "typesafe-stale-lock-"));
    const now = new Date("2026-09-16T21:00:00Z");
    const stale = now.getTime() - 60_000;
    const deadProcess = Bun.spawn([process.execPath, "-e", ""]);
    const deadPid = deadProcess.pid;
    await deadProcess.exited;
    try {
      writeFileSync(
        join(root, "quota.lock"),
        `${JSON.stringify({ pid: deadPid, token: "fresh-dead-owner", created_at_ms: now.getTime() })}\n`,
        "utf8",
      );
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
        now,
      )).toMatchObject({ allowed: false, reason: "quota_lock_busy" });
      rmSync(join(root, "quota.lock"));

      writeFileSync(
        join(root, "quota.lock"),
        `${JSON.stringify({ pid: process.pid, token: "stale-live-owner", created_at_ms: stale })}\n`,
        "utf8",
      );
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
        now,
      )).toMatchObject({ allowed: false, reason: "quota_lock_busy" });
      rmSync(join(root, "quota.lock"));

      writeFileSync(
        join(root, "quota.lock"),
        `${JSON.stringify({ pid: deadPid, token: "stale-dead-owner", created_at_ms: stale })}\n`,
        "utf8",
      );
      writeFileSync(
        join(root, "quota.lock.reclaim"),
        `${JSON.stringify({ pid: deadPid, token: "stale-reclaimer", created_at_ms: stale })}\n`,
        "utf8",
      );
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
        now,
      ).allowed).toBe(true);
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });


  test("quota reclaim close errors do not escape the reservation boundary", async () => {
    const root = mkdtempSync(join(tmpdir(), "typesafe-reclaim-close-"));
    const deadProcess = Bun.spawn([process.execPath, "-e", ""]);
    const deadPid = deadProcess.pid;
    await deadProcess.exited;
    const closeDescriptor = Object.getOwnPropertyDescriptor(Database.prototype, "close");
    if (!closeDescriptor || typeof closeDescriptor.value !== "function") {
      throw new Error("Database.close descriptor unavailable");
    }
    let closeCalls = 0;
    Object.defineProperty(Database.prototype, "close", {
      ...closeDescriptor,
      value(this: Database) {
        closeCalls += 1;
        closeDescriptor.value.call(this);
        throw new Error("injected close failure");
      },
    });
    try {
      writeFileSync(
        join(root, "quota.lock"),
        `${JSON.stringify({ pid: deadPid, token: "dead-owner", created_at_ms: Date.now() - 60_000 })}\n`,
        "utf8",
      );
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
      ).allowed).toBe(true);
      expect(closeCalls).toBe(1);
    } finally {
      Object.defineProperty(Database.prototype, "close", closeDescriptor);
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("failed reclaim commit releases its newly owned lock", async () => {
    const root = mkdtempSync(join(tmpdir(), "typesafe-reclaim-commit-"));
    const deadProcess = Bun.spawn([process.execPath, "-e", ""]);
    const deadPid = deadProcess.pid;
    await deadProcess.exited;
    const execDescriptor = Object.getOwnPropertyDescriptor(Database.prototype, "exec");
    if (!execDescriptor || typeof execDescriptor.value !== "function") {
      throw new Error("Database.exec descriptor unavailable");
    }
    let commitFailures = 0;
    try {
      Object.defineProperty(Database.prototype, "exec", {
        ...execDescriptor,
        value(this: Database, sql: string) {
          if (sql === "COMMIT") {
            commitFailures += 1;
            throw new Error("injected commit failure");
          }
          return execDescriptor.value.call(this, sql);
        },
      });
      writeFileSync(
        join(root, "quota.lock"),
        `${JSON.stringify({ pid: deadPid, token: "dead-owner", created_at_ms: Date.now() - 60_000 })}\n`,
        "utf8",
      );
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
      )).toMatchObject({ allowed: false, reason: "quota_lock_busy" });
      expect(commitFailures).toBe(1);
      Object.defineProperty(Database.prototype, "exec", execDescriptor);
      expect(reserveGlobalQuota(
        { request: "r", response: "s", evidence: [] },
        quotaOptions(root),
      ).allowed).toBe(true);
    } finally {
      Object.defineProperty(Database.prototype, "exec", execDescriptor);
      rmSync(root, { recursive: true, force: true });
    }
  });
  test("concurrent quota reservations never exceed the shared limit", async () => {
    const root = mkdtempSync(join(tmpdir(), "typesafe-quota-race-"));
    const worker = join(import.meta.dir, "..", "scripts", "quota-worker.ts");
    try {
      for (let round = 0; round < 5; round += 1) {
        const roundRoot = join(root, String(round));
        const barrier = join(roundRoot, "start");
        mkdirSync(roundRoot);
        const workers = Array.from({ length: 8 }, () => {
          const child = Bun.spawn(
            [process.execPath, worker, roundRoot, barrier],
            { stdout: "pipe", stderr: "pipe" },
          );
          return { process: child, reader: child.stdout.getReader() };
        });
        await Promise.all(workers.map(async ({ reader }) => {
          const ready = await reader.read();
          if (ready.done || new TextDecoder().decode(ready.value).trim() !== "READY") {
            throw new Error("quota worker did not reach the start barrier");
          }
        }));
        writeFileSync(barrier, "", { flag: "wx" });
        const results = await Promise.all(workers.map(async ({ process, reader }) => {
          const decoder = new TextDecoder();
          let output = "";
          while (true) {
            const chunk = await reader.read();
            if (chunk.done) break;
            output += decoder.decode(chunk.value, { stream: true });
          }
          output += decoder.decode();
          const error = await new Response(process.stderr).text();
          const exitCode = await process.exited;
          if (exitCode !== 0) throw new Error(error || output);
          return JSON.parse(output);
        }));
        const quota = JSON.parse(readFileSync(join(roundRoot, "quota.json"), "utf8"));
        const allowed = results.filter((result) => result.allowed).length;
        expect(quota.calls).toBe(2);
        expect(allowed).toBe(2);
      }
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });
});

describe("TypeSafe wire contract", () => {
  test("sends the System One request and validates all five Noul answers", async () => {
    const previous = process.env.TYPESAFE_API_KEY;
    process.env.TYPESAFE_API_KEY = "test-key";
    try {
      const result = await verifyStateLive(
        { request: "request", response: "response", evidence: [] },
        async (_input, init) => {
          expect(init?.headers).toEqual({
            Authorization: "Bearer test-key",
            "Content-Type": "application/json",
          });
          const body = JSON.parse(String(init?.body));
          expect(body.model).toBe("jev-latest");
          expect(Object.keys(body.questions)).toHaveLength(5);
          const answers = Object.fromEntries(
            Object.entries(safeAnswers).map(([key, noul]) => [key, { type: "noul", noul }]),
          );
          return new Response(JSON.stringify({ model: "jev-test", answers }), { status: 200 });
        },
      );
      expect(result).toEqual({ model: "jev-test", answers: safeAnswers });
    } finally {
      if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
      else process.env.TYPESAFE_API_KEY = previous;
    }
  });
});

describe("OMP lifecycle wiring", () => {
  test("default mode is off and performs no outbound verification", async () => {
    const handlers = new Map<string, Function>();
    let calls = 0;
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      registerTool() {},
      registerCommand() {},
      appendEntry() {},
      zod: {
        object: (value: unknown) => value,
        string: () => ({ describe() { return this; }, optional() { return this; } }),
        array: (item: unknown) => ({ item, describe() { return this; }, optional() { return this; } }),
      },
    };
    registerExtension(pi as never, {
      mode: "off",
      verify: async () => { calls += 1; return safeAnswers; },
    });
    const result = await handlers.get("session_stop")?.({ stop_hook_active: false }, {
      sessionManager: { getBranch: () => [message("user", "hello"), message("assistant", "hello") ] },
      ui: { notify() {} },
    });
    expect(result).toBeUndefined();
    expect(calls).toBe(0);
  });

  test("shadow mode records review without forcing continuation", async () => {
    const handlers = new Map<string, Function>();
    const receipts: unknown[] = [];
    const root = mkdtempSync(join(tmpdir(), "typesafe-shadow-"));
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      registerTool() {},
      registerCommand() {},
      appendEntry(_kind: string, value: unknown) { receipts.push(value); },
      zod: {
        object: (value: unknown) => value,
        string: () => ({ describe() { return this; }, optional() { return this; } }),
        array: (item: unknown) => ({ item, describe() { return this; }, optional() { return this; } }),
      },
    };
    try {
      registerExtension(pi as never, {
        mode: "shadow",
        quota: quotaOptions(root),
        verify: async (state) => {
          const outbound = JSON.stringify(state);
          for (const secret of ["quoted-env-secret", "json-password", "assistant-access"]) {
            if (outbound.includes(secret)) throw new Error(`verifier received raw secret: ${secret}`);
          }
          return { ...safeAnswers, overstates_completion: 0.87 };
        },
      });
      const result = await handlers.get("session_stop")?.({ stop_hook_active: false }, {
        sessionManager: { getBranch: () => [
          message("user", 'Is it fixed? TYPESAFE_API_KEY="quoted-env-secret"'),
          message("toolResult", '{"password":"json-password"}', "bash"),
          message("assistant", 'It is fixed and passing. access_token="assistant-access"'),
        ] },
        ui: { notify() {} },
      });
      const serializedReceipt = JSON.stringify(receipts[0]);
      for (const raw of ["Is it fixed?", "test failed", "It is fixed and passing.", "quoted-env-secret", "json-password", "assistant-access"]) {
        if (serializedReceipt.includes(raw)) throw new Error(`receipt retained raw payload: ${raw}`);
      }
      expect(result).toBeUndefined();
      expect(receipts).toHaveLength(1);
      expect(receipts[0]).toMatchObject({ advisory_only: true, verdict: "review", trigger: "overstates_completion" });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("shadow budget caps automatic calls", async () => {
    const handlers = new Map<string, Function>();
    const receipts: unknown[] = [];
    const root = mkdtempSync(join(tmpdir(), "typesafe-process-cap-"));
    let calls = 0;
    const pi = {
      on(name: string, handler: Function) { handlers.set(name, handler); },
      registerTool() {},
      registerCommand() {},
      appendEntry(_kind: string, value: unknown) { receipts.push(value); },
      zod: {
        object: (value: unknown) => value,
        string: () => ({ describe() { return this; }, optional() { return this; } }),
        array: (item: unknown) => ({ item, describe() { return this; }, optional() { return this; } }),
      },
    };
    try {
      registerExtension(pi as never, {
        mode: "shadow",
        maxAutomaticCalls: 1,
        quota: quotaOptions(root),
        verify: async () => { calls += 1; return safeAnswers; },
      });
      const ctx = {
        sessionManager: { getBranch: () => [message("user", "hello"), message("assistant", "hello")] },
        ui: { notify() {} },
      };
      await handlers.get("session_stop")?.({ stop_hook_active: false }, ctx);
      await handlers.get("session_stop")?.({ stop_hook_active: false }, ctx);
      expect(calls).toBe(1);
      expect(receipts).toHaveLength(2);
      expect(receipts[1]).toMatchObject({ advisory_only: true, verdict: "budget_exhausted", automatic_call_limit: 1 });
    } finally {
      rmSync(root, { recursive: true, force: true });
    }
  });

  test("busy and corrupt global quota never call Jev", async () => {
    const deadProcess = Bun.spawn([process.execPath, "-e", ""]);
    const deadPid = deadProcess.pid;
    await deadProcess.exited;
    const failures = [
      { fixture: "quota_lock_busy", reason: "quota_lock_busy" },
      { fixture: "quota_state_invalid", reason: "quota_state_invalid" },
      { fixture: "quota_reclaim_unavailable", reason: "quota_lock_busy" },
    ] as const;
    for (const failure of failures) {
      const handlers = new Map<string, Function>();
      const receipts: unknown[] = [];
      const root = mkdtempSync(join(tmpdir(), `typesafe-${failure.fixture}-`));
      let calls = 0;
      if (failure.fixture === "quota_lock_busy") {
        writeFileSync(join(root, "quota.lock"), "other-owner", "utf8");
      } else if (failure.fixture === "quota_state_invalid") {
        writeFileSync(join(root, "quota.json"), "{}\n", "utf8");
      } else {
        writeFileSync(
          join(root, "quota.lock"),
          `${JSON.stringify({ pid: deadPid, token: "dead-owner", created_at_ms: Date.now() - 60_000 })}\n`,
          "utf8",
        );
        mkdirSync(join(root, "quota.lock.reclaim.sqlite"));
      }
      const pi = {
        on(name: string, handler: Function) { handlers.set(name, handler); },
        registerTool() {},
        registerCommand() {},
        appendEntry(_kind: string, value: unknown) { receipts.push(value); },
        zod: {
          object: (value: unknown) => value,
          string: () => ({ describe() { return this; }, optional() { return this; } }),
          array: (item: unknown) => ({ item, describe() { return this; }, optional() { return this; } }),
        },
      };
      try {
        registerExtension(pi as never, {
          mode: "shadow",
          quota: quotaOptions(root),
          verify: async () => { calls += 1; return safeAnswers; },
        });
        await handlers.get("session_stop")?.({ stop_hook_active: false }, {
          sessionManager: { getBranch: () => [message("user", "hello"), message("assistant", "hello")] },
          ui: { notify() {} },
        });
        expect(calls).toBe(0);
        expect(receipts[0]).toMatchObject({ advisory_only: true, reason: failure.reason });
      } finally {
        rmSync(root, { recursive: true, force: true });
      }
    }
  });

  test("tool discloses export and status reports launch surface", async () => {
    let tool: unknown;
    let statusCommand: unknown;
    const notifications: string[] = [];
    const previousPane = process.env.ORCA_PANE_KEY;
    const pi = {
      on() {},
      registerTool(definition: unknown) { tool = definition; },
      registerCommand(_name: string, definition: unknown) { statusCommand = definition; },
      appendEntry() {},
      zod: {
        object: (value: unknown) => value,
        string: () => ({ describe() { return this; }, optional() { return this; } }),
        array: (item: unknown) => ({ item, describe() { return this; }, optional() { return this; } }),
      },
    };
    registerExtension(pi as never, { mode: "off", verify: async () => safeAnswers });
    expect(tool).toMatchObject({ approval: "exec" });
    expect(String(asRecord(tool).description)).toContain("api.typesafe.ai");
    process.env.ORCA_PANE_KEY = "test-pane";
    try {
      const handler = asRecord(statusCommand).handler;
      if (typeof handler !== "function") throw new Error("status command handler missing");
      await handler("", { ui: { notify(message: string) { notifications.push(message); } } });
      expect(notifications[0]).toContain("Orca-launched OMP");
    } finally {
      if (previousPane === undefined) delete process.env.ORCA_PANE_KEY;
      else process.env.ORCA_PANE_KEY = previousPane;
    }
  });
});
