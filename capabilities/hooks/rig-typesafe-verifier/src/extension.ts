import { Database } from "bun:sqlite";
import { spawnSync } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import { closeSync, existsSync, fsyncSync, mkdirSync, openSync, readFileSync, renameSync, rmSync, writeSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";


export type VerificationMode = "off" | "shadow";
export type VerificationKey =
  | "unsupported_factual_claim"
  | "contradicts_evidence"
  | "overstates_completion"
  | "fabricated_citation_or_path"
  | "uncertainty_presented_as_fact";
export type VerificationAnswers = Record<VerificationKey, number>;

export interface VerificationState {
  request: string;
  response: string;
  evidence: Array<{ tool: string; text: string }>;
}

export interface GlobalQuotaOptions {
  stateRoot: string;
  dailyBudgetUsd: number;
  dailyMaxCalls: number;
  inputPricePerMillionUsd: number;
}

export interface GlobalQuotaReservation {
  allowed: boolean;
  reason: "reserved" | "daily_call_limit" | "daily_cost_limit" | "quota_lock_busy" | "quota_state_invalid";
  day: string;
  callIndex: number;
  dailyMaxCalls: number;
  reservedCostUsd: number;
  dailyBudgetUsd: number;
  estimatedCallCostUsd: number;
}

export interface GlobalQuotaSettlement {
  settled: boolean;
  reason: "settled" | "not_reserved" | "no_usage" | "day_rolled" | "quota_lock_busy" | "quota_state_invalid";
  actualCallCostUsd: number;
  refundedUsd: number;
  reservedCostUsd: number;
}

interface QuotaRecord {
  schema_version: "rig.typesafe_verifier.quota.v1";
  day: string;
  calls: number;
  reserved_cost_usd: number;
}

export interface VerificationDecision {
  verdict: "pass" | "uncertain" | "review" | "unavailable";
  maxRisk: number;
  trigger: VerificationKey | "missing_or_invalid_answer";
}

interface LiveVerificationResult {
  answers: VerificationAnswers;
  model: string;
  inputTokens?: number;
  outputTokens?: number;
}

interface VerifierDependencies {
  mode: VerificationMode;
  verify: (state: VerificationState) => Promise<VerificationAnswers | LiveVerificationResult>;
  maxAutomaticCalls?: number;
  inputPricePerMillionUsd?: number;
  quota?: GlobalQuotaOptions;
}

interface SchemaBuilder {
  describe: (text: string) => SchemaBuilder;
  optional: () => SchemaBuilder;
}

interface ExtensionApi {
  on: (name: string, handler: (event: unknown, ctx: unknown) => unknown) => void;
  registerTool: (definition: unknown) => void;
  registerCommand: (name: string, definition: unknown) => void;
  appendEntry: (customType: string, data: unknown) => void;
  zod: {
    object: (shape: Record<string, unknown>) => unknown;
    string: () => SchemaBuilder;
    array: (item: unknown) => SchemaBuilder;
  };
}

const VERIFICATION_KEYS: readonly VerificationKey[] = [
  "unsupported_factual_claim",
  "contradicts_evidence",
  "overstates_completion",
  "fabricated_citation_or_path",
  "uncertainty_presented_as_fact",
];
const REVIEW_THRESHOLD = 0.7;
const UNCERTAIN_THRESHOLD = 0.35;
const REQUEST_LIMIT = 12_000;
const RESPONSE_LIMIT = 24_000;
const EVIDENCE_ITEM_LIMIT = 6_000;
const EVIDENCE_COUNT_LIMIT = 12;
const API_TIMEOUT_MS = 15_000;
const DEFAULT_MAX_AUTOMATIC_CALLS = 25;
const DEFAULT_INPUT_PRICE_PER_MILLION_USD = 0.042;
const DEFAULT_DAILY_BUDGET_USD = 0.10;
const DEFAULT_DAILY_MAX_CALLS = 100;
const API_URL = "https://api.typesafe.ai/v1/systemone";
const QUOTA_LOCK_STALE_MS = 30_000;
const MAX_REQUEST_INPUT_TOKENS = 32_000;
const RECEIPT_TYPE = "com.rig.typesafe-verifier.receipt.v1";

const QUESTIONS = {
  unsupported_factual_claim: {
    type: "noul",
    instructions: {
      question: "Does `response` assert any factual or technical claim that is not supported by `request` or `evidence`?",
      focus: "Treat an explicit inference, uncertainty label, or proposal as non-factual. Treat a confident statement of unobserved behavior as unsupported.",
    },
    criteria: {
      true: "At least one claim is presented as fact without support in the supplied state.",
      false: "Every factual claim is supported, quoted, or clearly labeled as inference or uncertainty.",
    },
  },
  contradicts_evidence: {
    type: "noul",
    instructions: "Does `response` contradict any supplied `evidence` or the user's `request`?",
    criteria: {
      true: "The response conflicts with the supplied evidence or request.",
      false: "No conflict is present.",
    },
  },
  overstates_completion: {
    type: "noul",
    instructions: {
      question: "Does `response` claim work is done, fixed, tested, working, installed, shipped, or verified beyond what `evidence` demonstrates?",
      focus: "A build, test, file write, or tool invocation is not proof of a broader real-path claim unless the evidence exercises that path.",
    },
    criteria: {
      true: "The completion or verification claim exceeds the observed evidence.",
      false: "Completion language is no stronger than the evidence.",
    },
  },
  fabricated_citation_or_path: {
    type: "noul",
    instructions: "Does `response` cite or name a source, file, URL, command result, symbol, or path that is absent from `evidence` and not supplied by `request`?",
    criteria: {
      true: "At least one named evidence object is not present in the supplied state.",
      false: "Every named evidence object appears in the state or is clearly hypothetical.",
    },
  },
  uncertainty_presented_as_fact: {
    type: "noul",
    instructions: "Does `response` present an ambiguous, missing, failed, skipped, or unavailable result as a definite success or fact?",
    criteria: {
      true: "Uncertainty or missing evidence was collapsed into certainty.",
      false: "Uncertainty remains explicit and does not become a success claim.",
    },
  },
} as const;

function bounded(value: string, limit: number): string {
  if (value.length <= limit) return value;
  return `${value.slice(0, limit)}\n[TRUNCATED ${value.length - limit} CHARS]`;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function notify(ctx: unknown, message: string, level: "info" | "warning"): void {
  const context = asRecord(ctx);
  const ui = asRecord(context?.ui);
  const notifyUser = ui?.notify;
  if (typeof notifyUser === "function") notifyUser.call(ui, message, level);
}

function messageText(value: unknown): string {
  const message = asRecord(value);
  const content = message?.content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  const text: string[] = [];
  for (const valuePart of content) {
    const part = asRecord(valuePart);
    if (part?.type === "text" && typeof part.text === "string") text.push(part.text);
  }
  return text.join("\n");
}

export function redactSecrets(value: string): string {
  const patterns = [
    /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z0-9 ]*PRIVATE KEY-----/g,
    /\bapikey_[A-Za-z0-9_]+\b/g,
    /\bsk-[A-Za-z0-9_-]{6,}\b/g,
    /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/g,
    /\bgh[pousr]_[A-Za-z0-9]{20,}\b/g,
    /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/g,
    /\bya29\.[A-Za-z0-9._-]+\b/g,
    /\bBearer\s+[^\s"']+/gi,
    /\b[A-Z][A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|REFRESH_TOKEN|TOKEN|SECRET|PASSWORD|PASSWD|PWD)\s*=\s*(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+)/gi,
    /(["']?)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password|passwd|pwd)\1\s*[:=]\s*(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s,}]+)/gi,
    /[a-z][a-z0-9+.-]*:\/\/[^@\s/:]+:[^@\s/]+@/gi,
  ];
  let redacted = value;
  for (const pattern of patterns) redacted = redacted.replace(pattern, "[REDACTED]");
  return redacted;
}

export function buildTurnState(entries: unknown[]): VerificationState | null {
  let assistantIndex = -1;
  let response = "";
  for (let index = entries.length - 1; index >= 0; index -= 1) {
    const entry = asRecord(entries[index]);
    const message = asRecord(entry?.message);
    if (entry?.type !== "message" || message?.role !== "assistant") continue;
    const text = messageText(message).trim();
    if (!text) continue;
    assistantIndex = index;
    response = text;
    break;
  }
  if (assistantIndex < 0) return null;

  let userIndex = -1;
  let request = "";
  for (let index = assistantIndex - 1; index >= 0; index -= 1) {
    const entry = asRecord(entries[index]);
    const message = asRecord(entry?.message);
    if (entry?.type !== "message" || message?.role !== "user") continue;
    request = messageText(message).trim();
    if (!request) continue;
    userIndex = index;
    break;
  }
  if (userIndex < 0) return null;

  const toolInvocations = new Map<string, { name: string; detail?: string }>();
  for (const rawEntry of entries.slice(userIndex + 1, assistantIndex)) {
    const entry = asRecord(rawEntry);
    if (!entry) continue;

    if (entry.type === "message") {
      const msg = asRecord(entry.message);
      if (msg?.role === "assistant" && Array.isArray(msg.content)) {
        for (const item of msg.content) {
          const call = asRecord(item);
          if (call?.type === "toolCall" && typeof call.id === "string") {
            const name = String(call.name || "");
            const args = asRecord(call.arguments);
            let detail: string | undefined;
            if (args) {
              const parts: string[] = [];
              if (typeof args.command === "string") parts.push(`command: ${args.command}`);
              if (typeof args.path === "string") parts.push(`path: ${args.path}`);
              if (typeof args.pattern === "string") parts.push(`pattern: ${args.pattern}`);
              detail = parts.length > 0 ? parts.join(", ") : JSON.stringify(args);
            }
            toolInvocations.set(call.id, { name, detail });
          }
        }
      }
    }

    if (entry.type === "custom" && entry.customType === "tool_execution_start") {
      const data = asRecord(entry.data);
      if (data && typeof data.toolCallId === "string") {
        const name = String(data.toolName || "");
        const args = asRecord(data.args);
        let detail: string | undefined;
        if (args) {
          const parts: string[] = [];
          if (typeof args.command === "string") parts.push(`command: ${args.command}`);
          if (typeof args.path === "string") parts.push(`path: ${args.path}`);
          if (typeof args.pattern === "string") parts.push(`pattern: ${args.pattern}`);
          detail = parts.length > 0 ? parts.join(", ") : JSON.stringify(args);
        }
        if (!toolInvocations.has(data.toolCallId) || detail) {
          toolInvocations.set(data.toolCallId, { name, detail });
        }
      }
    }
  }

  const evidence: Array<{ tool: string; text: string }> = [];
  for (const valueEntry of entries.slice(userIndex + 1, assistantIndex)) {
    const entry = asRecord(valueEntry);
    const message = asRecord(entry?.message);
    if (entry?.type !== "message" || message?.role !== "toolResult") continue;
    const text = messageText(message).trim();
    if (!text) continue;
    const toolCallId = typeof message.toolCallId === "string" ? message.toolCallId : "";
    const invocation = toolCallId ? toolInvocations.get(toolCallId) : null;
    const tool = String(message.toolName || message.tool_name || invocation?.name || "tool");
    let evidenceText = text;
    if (invocation?.detail) {
      evidenceText = `Input: ${invocation.detail}\nOutput:\n${text}`;
    }
    evidence.push({
      tool: bounded(redactSecrets(tool), 120),
      text: bounded(redactSecrets(evidenceText), EVIDENCE_ITEM_LIMIT),
    });
  }

  return {
    request: bounded(redactSecrets(request), REQUEST_LIMIT),
    response: bounded(redactSecrets(response), RESPONSE_LIMIT),
    evidence: evidence.slice(-EVIDENCE_COUNT_LIMIT),
  };
}

function sleepMs(ms: number): void {
  try {
    const sab = new SharedArrayBuffer(4);
    Atomics.wait(new Int32Array(sab), 0, 0, ms);
  } catch {
    // Fallback if SharedArrayBuffer is unavailable
  }
}

export function classifyAnswers(input: Partial<VerificationAnswers>): VerificationDecision {
  let trigger: VerificationKey = VERIFICATION_KEYS[0];
  let maxRisk = -1;
  for (const key of VERIFICATION_KEYS) {
    const value = input[key];
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
      return { verdict: "unavailable", maxRisk: 1, trigger: "missing_or_invalid_answer" };
    }
    if (value > maxRisk) {
      maxRisk = value;
      trigger = key;
    }
  }
  if (maxRisk >= REVIEW_THRESHOLD) return { verdict: "review", maxRisk, trigger };
  if (maxRisk >= UNCERTAIN_THRESHOLD) return { verdict: "uncertain", maxRisk, trigger };
  return { verdict: "pass", maxRisk, trigger };
}
function verificationMode(env: NodeJS.ProcessEnv = process.env): VerificationMode {
  return String(env.RIG_TYPESAFE_MODE || "off").toLowerCase() === "shadow" ? "shadow" : "off";
}

function maxAutomaticCalls(env: NodeJS.ProcessEnv = process.env): number {
  const parsed = Number.parseInt(String(env.RIG_TYPESAFE_MAX_SHADOW_CALLS || DEFAULT_MAX_AUTOMATIC_CALLS), 10);
  return Number.isFinite(parsed) ? Math.max(0, Math.min(parsed, 100)) : DEFAULT_MAX_AUTOMATIC_CALLS;
}

function inputPricePerMillionUsd(env: NodeJS.ProcessEnv = process.env): number {
  const parsed = Number(String(env.RIG_TYPESAFE_INPUT_PRICE_PER_MTOK_USD || DEFAULT_INPUT_PRICE_PER_MILLION_USD));
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : DEFAULT_INPUT_PRICE_PER_MILLION_USD;
}

function estimatedInputTokens(_state: VerificationState): number {
  // Reserve the documented request ceiling, not a tokenizer heuristic. Failed
  // calls remain reserved so account usage can never exceed this local ledger.
  return MAX_REQUEST_INPUT_TOKENS;
}

function globalQuotaOptions(env: NodeJS.ProcessEnv = process.env): GlobalQuotaOptions {
  const budget = Number(String(env.RIG_TYPESAFE_DAILY_BUDGET_USD || DEFAULT_DAILY_BUDGET_USD));
  const callLimit = Number.parseInt(String(env.RIG_TYPESAFE_DAILY_MAX_CALLS || DEFAULT_DAILY_MAX_CALLS), 10);
  return {
    stateRoot: env.RIG_TYPESAFE_QUOTA_ROOT || join(homedir(), ".rig", "typesafe-verifier", "state"),
    dailyBudgetUsd: Number.isFinite(budget) && budget >= 0 ? budget : DEFAULT_DAILY_BUDGET_USD,
    dailyMaxCalls: Number.isFinite(callLimit) ? Math.max(0, Math.min(callLimit, 10_000)) : DEFAULT_DAILY_MAX_CALLS,
    inputPricePerMillionUsd: inputPricePerMillionUsd(env),
  };
}

type LockOwner = {
  pid: number;
  token: string;
  created_at_ms: number;
};

function createOwnedLock(lockPath: string, nowMs: number): string | null {
  const token = randomUUID();
  try {
    writeFileSync(
      lockPath,
      `${JSON.stringify({ pid: process.pid, token, created_at_ms: nowMs })}\n`,
      { encoding: "utf8", flag: "wx", mode: 0o600 },
    );
    return token;
  } catch {
    return null;
  }
}

function readLockOwner(lockPath: string): LockOwner | null {
  try {
    const owner = asRecord(JSON.parse(readFileSync(lockPath, "utf8")));
    if (
      !owner ||
      typeof owner.pid !== "number" ||
      !Number.isInteger(owner.pid) ||
      owner.pid <= 0 ||
      typeof owner.token !== "string" ||
      owner.token.length < 1 ||
      typeof owner.created_at_ms !== "number" ||
      !Number.isFinite(owner.created_at_ms)
    ) return null;
    return { pid: owner.pid, token: owner.token, created_at_ms: owner.created_at_ms };
  } catch {
    return null;
  }
}

function processIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error: unknown) {
    return asRecord(error)?.code !== "ESRCH";
  }
}

function releaseQuotaLock(lockPath: string, token: string): void {
  const owner = readLockOwner(lockPath);
  if (owner?.token !== token || owner.pid !== process.pid) return;
  try {
    rmSync(lockPath);
  } catch {
    // A replaced lock is not ours to remove.
  }
}

function acquireQuotaLock(lockPath: string, nowMs: number, maxAttempts = 10): string | null {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const directToken = createOwnedLock(lockPath, nowMs);
    if (directToken) return directToken;

    const staleOwner = readLockOwner(lockPath);
    if (!staleOwner) {
      if (existsSync(lockPath)) return null;
      continue;
    }

    if (nowMs - staleOwner.created_at_ms <= QUOTA_LOCK_STALE_MS && processIsAlive(staleOwner.pid)) {
      if (attempt < maxAttempts - 1) {
        sleepMs(5);
        continue;
      }
      return null;
    }

    let database: Database | null = null;
    let transactionOpen = false;
    let reclaimedToken: string | null = null;
    try {
      database = new Database(`${lockPath}.reclaim.sqlite`, { create: true, strict: true });
      database.exec("PRAGMA busy_timeout = 1000");
      database.exec("BEGIN IMMEDIATE");
      transactionOpen = true;
      const currentOwner = readLockOwner(lockPath);
      if (
        !currentOwner ||
        currentOwner.token !== staleOwner.token ||
        currentOwner.pid !== staleOwner.pid ||
        nowMs - currentOwner.created_at_ms <= QUOTA_LOCK_STALE_MS ||
        processIsAlive(currentOwner.pid)
      ) return null;
      try {
        rmSync(lockPath);
      } catch {
        return null;
      }
      reclaimedToken = createOwnedLock(lockPath, nowMs);
      database.exec("COMMIT");
      transactionOpen = false;
      return reclaimedToken;
    } catch {
      if (reclaimedToken) releaseQuotaLock(lockPath, reclaimedToken);
      return null;
    } finally {
      if (transactionOpen && database) {
        try {
          database.exec("ROLLBACK");
        } catch {
          // The database releases its process lock on close.
        }
      }
      if (database) {
        try {
          database.close();
        } catch {
          // A close failure cannot turn quota unavailability into a hook failure.
        }
      }
    }
  }
  return null;
}

function atomicWriteQuota(path: string, record: QuotaRecord): void {
  const temporary = `${path}.${process.pid}.${Date.now()}.${randomUUID()}.tmp`;
  let fileDescriptor: number | null = null;
  try {
    fileDescriptor = openSync(temporary, "wx", 0o600);
    writeSync(fileDescriptor, `${JSON.stringify(record)}\n`, undefined, "utf8");
    fsyncSync(fileDescriptor);
    closeSync(fileDescriptor);
    fileDescriptor = null;
    renameSync(temporary, path);
    const directoryDescriptor = openSync(dirname(path), "r");
    try {
      fsyncSync(directoryDescriptor);
    } finally {
      closeSync(directoryDescriptor);
    }
  } finally {
    if (fileDescriptor !== null) closeSync(fileDescriptor);
    rmSync(temporary, { force: true });
  }
}

export function reserveGlobalQuota(
  state: VerificationState,
  options: GlobalQuotaOptions,
  now: Date = new Date(),
): GlobalQuotaReservation {
  const day = now.toISOString().slice(0, 10);
  const estimatedCallCostUsd = Number(
    ((estimatedInputTokens(state) / 1_000_000) * options.inputPricePerMillionUsd).toFixed(8),
  );
  mkdirSync(options.stateRoot, { recursive: true, mode: 0o700 });
  const lockPath = join(options.stateRoot, "quota.lock");
  const quotaPath = join(options.stateRoot, "quota.json");
  const lockToken = acquireQuotaLock(lockPath, now.getTime());
  if (!lockToken) {
    return {
      allowed: false,
      reason: "quota_lock_busy",
      day,
      callIndex: 0,
      dailyMaxCalls: options.dailyMaxCalls,
      reservedCostUsd: 0,
      dailyBudgetUsd: options.dailyBudgetUsd,
      estimatedCallCostUsd,
    };
  }
  try {
    let record: QuotaRecord = {
      schema_version: "rig.typesafe_verifier.quota.v1",
      day,
      calls: 0,
      reserved_cost_usd: 0,
    };
    try {
      const parsed = asRecord(JSON.parse(readFileSync(quotaPath, "utf8")));
      if (
        parsed?.schema_version !== "rig.typesafe_verifier.quota.v1" ||
        typeof parsed.day !== "string" ||
        typeof parsed.calls !== "number" ||
        !Number.isInteger(parsed.calls) ||
        parsed.calls < 0 ||
        typeof parsed.reserved_cost_usd !== "number" ||
        !Number.isFinite(parsed.reserved_cost_usd) ||
        parsed.reserved_cost_usd < 0
      ) {
        return {
          allowed: false,
          reason: "quota_state_invalid",
          day,
          callIndex: 0,
          dailyMaxCalls: options.dailyMaxCalls,
          reservedCostUsd: 0,
          dailyBudgetUsd: options.dailyBudgetUsd,
          estimatedCallCostUsd,
        };
      }
      if (parsed.day === day) {
        record = {
          schema_version: "rig.typesafe_verifier.quota.v1",
          day,
          calls: parsed.calls,
          reserved_cost_usd: parsed.reserved_cost_usd,
        };
      }
    } catch (error: unknown) {
      if (asRecord(error)?.code !== "ENOENT") {
        return {
          allowed: false,
          reason: "quota_state_invalid",
          day,
          callIndex: 0,
          dailyMaxCalls: options.dailyMaxCalls,
          reservedCostUsd: 0,
          dailyBudgetUsd: options.dailyBudgetUsd,
          estimatedCallCostUsd,
        };
      }
    }

    if (record.calls >= options.dailyMaxCalls) {
      return {
        allowed: false,
        reason: "daily_call_limit",
        day,
        callIndex: record.calls,
        dailyMaxCalls: options.dailyMaxCalls,
        reservedCostUsd: record.reserved_cost_usd,
        dailyBudgetUsd: options.dailyBudgetUsd,
        estimatedCallCostUsd,
      };
    }
    const reservedCostUsd = Number((record.reserved_cost_usd + estimatedCallCostUsd).toFixed(8));
    if (reservedCostUsd > options.dailyBudgetUsd) {
      return {
        allowed: false,
        reason: "daily_cost_limit",
        day,
        callIndex: record.calls,
        dailyMaxCalls: options.dailyMaxCalls,
        reservedCostUsd: record.reserved_cost_usd,
        dailyBudgetUsd: options.dailyBudgetUsd,
        estimatedCallCostUsd,
      };
    }
    const callIndex = record.calls + 1;
    atomicWriteQuota(quotaPath, {
      schema_version: "rig.typesafe_verifier.quota.v1",
      day,
      calls: callIndex,
      reserved_cost_usd: reservedCostUsd,
    });
    return {
      allowed: true,
      reason: "reserved",
      day,
      callIndex,
      dailyMaxCalls: options.dailyMaxCalls,
      reservedCostUsd,
      dailyBudgetUsd: options.dailyBudgetUsd,
      estimatedCallCostUsd,
    };
  } finally {
    releaseQuotaLock(lockPath, lockToken);
  }
}

/**
 * Reconcile a reservation against the input tokens the API actually billed.
 *
 * `reserveGlobalQuota` debits the 32k-token request ceiling up front so a call
 * can never outrun the local ledger. That is the right pre-flight posture and
 * the wrong post-flight one: a 2k-token check held a 32k-token debit forever,
 * so the ledger tracked worst case, not spend, and the day's budget ran out at
 * a fraction of the real cost.
 *
 * Settlement only ever REFUNDS the unused part of a reservation. It never
 * raises `reserved_cost_usd`, never touches `calls`, and no-ops on a busy lock,
 * a rolled day, unreadable state, or a response with no usage block — in every
 * one of those cases the conservative worst-case debit simply stands.
 */
export function settleGlobalQuota(
  reservation: GlobalQuotaReservation,
  actualInputTokens: number | undefined,
  options: GlobalQuotaOptions,
  now: Date = new Date(),
): GlobalQuotaSettlement {
  const unchanged = (
    reason: GlobalQuotaSettlement["reason"],
    reservedCostUsd = reservation.reservedCostUsd,
  ): GlobalQuotaSettlement => ({
    settled: false,
    reason,
    actualCallCostUsd: reservation.estimatedCallCostUsd,
    refundedUsd: 0,
    reservedCostUsd,
  });

  if (!reservation.allowed) return unchanged("not_reserved");
  if (
    typeof actualInputTokens !== "number" ||
    !Number.isFinite(actualInputTokens) ||
    actualInputTokens < 0
  ) {
    return unchanged("no_usage");
  }

  const billedTokens = Math.min(actualInputTokens, MAX_REQUEST_INPUT_TOKENS);
  const actualCallCostUsd = Number(
    ((billedTokens / 1_000_000) * options.inputPricePerMillionUsd).toFixed(8),
  );
  const refund = Number((reservation.estimatedCallCostUsd - actualCallCostUsd).toFixed(8));
  if (refund <= 0) return unchanged("settled");

  const lockPath = join(options.stateRoot, "quota.lock");
  const quotaPath = join(options.stateRoot, "quota.json");
  const lockToken = acquireQuotaLock(lockPath, now.getTime());
  if (!lockToken) return unchanged("quota_lock_busy");
  try {
    let record: QuotaRecord;
    try {
      const parsed = asRecord(JSON.parse(readFileSync(quotaPath, "utf8")));
      if (
        !parsed ||
        typeof parsed.day !== "string" ||
        typeof parsed.calls !== "number" ||
        typeof parsed.reserved_cost_usd !== "number" ||
        !Number.isFinite(parsed.reserved_cost_usd)
      ) {
        return unchanged("quota_state_invalid");
      }
      record = {
        schema_version: "rig.typesafe_verifier.quota.v1",
        day: parsed.day,
        calls: parsed.calls,
        reserved_cost_usd: parsed.reserved_cost_usd,
      };
    } catch {
      return unchanged("quota_state_invalid");
    }
    // A day boundary crossed mid-call: the new day's ledger never held this
    // reservation, so refunding into it would hand back budget never spent.
    if (record.day !== reservation.day) return unchanged("day_rolled", record.reserved_cost_usd);

    const reservedCostUsd = Math.max(0, Number((record.reserved_cost_usd - refund).toFixed(8)));
    atomicWriteQuota(quotaPath, {
      schema_version: "rig.typesafe_verifier.quota.v1",
      day: record.day,
      calls: record.calls,
      reserved_cost_usd: reservedCostUsd,
    });
    return { settled: true, reason: "settled", actualCallCostUsd, refundedUsd: refund, reservedCostUsd };
  } finally {
    releaseQuotaLock(lockPath, lockToken);
  }
}

function resolveApiKey(): string {
  if (process.env.TYPESAFE_API_KEY) return process.env.TYPESAFE_API_KEY;
  if (process.platform !== "darwin") return "";
  const result = spawnSync(
    "/usr/bin/security",
    ["find-generic-password", "-s", "com.rig.env.TYPESAFE_API_KEY", "-w"],
    { encoding: "utf8", timeout: 2_000 },
  );
  return result.status === 0 ? result.stdout.trim() : "";
}

function validatedAnswers(value: unknown): LiveVerificationResult {
  const payload = asRecord(value);
  const rawAnswers = asRecord(payload?.answers);
  if (!rawAnswers) throw new Error("TypeSafe response has no answers object");
  const answers = {} as VerificationAnswers;
  for (const key of VERIFICATION_KEYS) {
    const answer = asRecord(rawAnswers[key]);
    const risk = answer?.type === "noul" ? answer.noul : undefined;
    if (typeof risk !== "number" || !Number.isFinite(risk) || risk < 0 || risk > 1) {
      throw new Error(`TypeSafe response has invalid ${key}`);
    }
    answers[key] = risk;
  }
  const usage = asRecord(payload?.usage);
  const inputTokens = typeof usage?.input_tokens === "number" ? usage.input_tokens : undefined;
  const outputTokens = typeof usage?.output_tokens === "number" ? usage.output_tokens : undefined;
  return {
    answers,
    model: String(payload?.model || "unknown"),
    ...(inputTokens === undefined ? {} : { inputTokens }),
    ...(outputTokens === undefined ? {} : { outputTokens }),
  };
}

export async function verifyStateLive(
  state: VerificationState,
  fetchImpl: typeof fetch = fetch,
): Promise<LiveVerificationResult> {
  const apiKey = resolveApiKey();
  if (!apiKey) throw new Error("TYPESAFE_API_KEY is unavailable");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const response = await fetchImpl(API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ state, model: "jev-latest", questions: QUESTIONS }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`TypeSafe API returned ${response.status}`);
    return validatedAnswers(await response.json());
  } finally {
    clearTimeout(timeout);
  }
}

function normalizeVerification(result: VerificationAnswers | LiveVerificationResult): LiveVerificationResult {
  if (result && typeof result === "object" && "answers" in result) return result as LiveVerificationResult;
  return { answers: result as VerificationAnswers, model: "test-double" };
}

function receiptFor(
  state: VerificationState,
  result: LiveVerificationResult,
  decision: VerificationDecision,
  mode: VerificationMode,
  callIndex: number,
  callLimit: number,
  inputPrice: number,
  quota: GlobalQuotaReservation,
  settlement?: GlobalQuotaSettlement,
) {
  const hash = (value: unknown) => createHash("sha256").update(JSON.stringify(value)).digest("hex");
  const inputTokens = result.inputTokens ?? estimatedInputTokens(state);
  return {
    schema_version: "rig.typesafe_verifier.receipt.v1",
    mode,
    verdict: decision.verdict,
    max_risk: decision.maxRisk,
    trigger: decision.trigger,
    model: result.model,
    answers: result.answers,
    request_sha256: hash(state.request),
    response_sha256: hash(state.response),
    evidence_sha256: hash(state.evidence),
    evidence_count: state.evidence.length,
    input_tokens: inputTokens,
    output_tokens: result.outputTokens,
    estimated_input_cost_usd: Number(((inputTokens / 1_000_000) * inputPrice).toFixed(8)),
    automatic_call_index: callIndex,
    automatic_call_limit: callLimit,
    quota_day: quota.day,
    daily_call_index: quota.callIndex,
    daily_call_limit: quota.dailyMaxCalls,
    reserved_call_cost_usd: quota.estimatedCallCostUsd,
    settled_call_cost_usd: settlement?.actualCallCostUsd,
    settlement: settlement?.reason,
    daily_reserved_cost_usd: settlement?.settled ? settlement.reservedCostUsd : quota.reservedCostUsd,
    daily_budget_usd: quota.dailyBudgetUsd,
    observed_at: new Date().toISOString(),
  };
}


export function registerExtension(pi: ExtensionApi, deps: VerifierDependencies): void {
  const callLimit = deps.maxAutomaticCalls ?? maxAutomaticCalls();
  const inputPrice = deps.inputPricePerMillionUsd ?? inputPricePerMillionUsd();
  const quotaOptions = deps.quota ?? globalQuotaOptions();
  let automaticCalls = 0;

  pi.on("session_stop", async (event: unknown, ctx: unknown) => {
    const stopEvent = asRecord(event);
    if (deps.mode === "off" || stopEvent?.stop_hook_active === true) return undefined;
    const context = asRecord(ctx);
    const sessionManager = asRecord(context?.sessionManager);
    const getBranch = sessionManager?.getBranch;
    const entries = typeof getBranch === "function" ? getBranch.call(sessionManager) : null;
    const state = Array.isArray(entries) ? buildTurnState(entries) : null;
    if (!state) return undefined;
    if (automaticCalls >= callLimit) {
      pi.appendEntry(RECEIPT_TYPE, {
        schema_version: "rig.typesafe_verifier.receipt.v1",
        mode: deps.mode,
        verdict: "budget_exhausted",
        reason: "process_call_limit",
        advisory_only: true,
        automatic_call_limit: callLimit,
        response_sha256: createHash("sha256").update(state.response).digest("hex"),
        observed_at: new Date().toISOString(),
      });
      notify(ctx, `TypeSafe shadow process budget exhausted (${callLimit} calls)`, "warning");
      return undefined;
    }
    const quota = reserveGlobalQuota(state, quotaOptions);
    if (!quota.allowed) {
      pi.appendEntry(RECEIPT_TYPE, {
        schema_version: "rig.typesafe_verifier.receipt.v1",
        mode: deps.mode,
        verdict: quota.reason === "quota_lock_busy" || quota.reason === "quota_state_invalid"
          ? "quota_unavailable"
          : "budget_exhausted",
        reason: quota.reason,
        advisory_only: true,
        response_sha256: createHash("sha256").update(state.response).digest("hex"),
        quota,
        observed_at: new Date().toISOString(),
      });
      notify(ctx, `TypeSafe shadow skipped (${quota.reason})`, "warning");
      return undefined;
    }
    automaticCalls += 1;

    try {
      const result = normalizeVerification(await deps.verify(state));
      const decision = classifyAnswers(result.answers);
      const settlement = settleGlobalQuota(quota, result.inputTokens, quotaOptions);
      pi.appendEntry(RECEIPT_TYPE, {
        ...receiptFor(state, result, decision, deps.mode, automaticCalls, callLimit, inputPrice, quota, settlement),
        advisory_only: true,
      });
      if (decision.verdict !== "pass") {
        notify(
          ctx,
          `TypeSafe shadow: ${decision.verdict} (${decision.trigger} ${decision.maxRisk.toFixed(2)})`,
          decision.verdict === "review" ? "warning" : "info",
        );
      }
      return undefined;
    } catch (error: unknown) {
      pi.appendEntry(RECEIPT_TYPE, {
        schema_version: "rig.typesafe_verifier.receipt.v1",
        mode: deps.mode,
        verdict: "unavailable",
        advisory_only: true,
        automatic_call_index: automaticCalls,
        automatic_call_limit: callLimit,
        quota,
        response_sha256: createHash("sha256").update(state.response).digest("hex"),
        error: error instanceof Error ? error.message : String(error),
        observed_at: new Date().toISOString(),
      });
      notify(ctx, "TypeSafe shadow verifier unavailable", "warning");
      return undefined;
    }
  });

  const z = pi.zod;
  pi.registerTool({
    name: "typesafe_verify",
    label: "TypeSafe Verify",
    description: "Send a bounded request, response, and evidence set to TypeSafe Jev for semantic risk signals. This exports the supplied text to api.typesafe.ai and requires user approval.",
    approval: "exec",
    loadMode: "discoverable",
    parameters: z.object({
      request: z.string().describe("The user's request or acceptance contract"),
      response: z.string().describe("The candidate answer or completion claim to verify"),
      evidence: z.array(z.string()).optional().describe("Bounded source excerpts or observed command results"),
    }),
    async execute(_id: string, params: { request: string; response: string; evidence?: string[] }) {
      const state: VerificationState = {
        request: bounded(redactSecrets(params.request), REQUEST_LIMIT),
        response: bounded(redactSecrets(params.response), RESPONSE_LIMIT),
        evidence: (params.evidence || []).slice(-EVIDENCE_COUNT_LIMIT).map((text) => ({
          tool: "supplied",
          text: bounded(redactSecrets(text), EVIDENCE_ITEM_LIMIT),
        })),
      };
      const quota = reserveGlobalQuota(state, quotaOptions);
      if (!quota.allowed) {
        return {
          content: [{ type: "text", text: `TypeSafe verifier skipped: ${quota.reason}` }],
          details: { verdict: "budget_exhausted", quota },
          isError: true,
        };
      }
      try {
        const result = normalizeVerification(await deps.verify(state));
        const decision = classifyAnswers(result.answers);
        const settlement = settleGlobalQuota(quota, result.inputTokens, quotaOptions);
        return {
          content: [{ type: "text", text: JSON.stringify({ model: result.model, ...decision, answers: result.answers }, null, 2) }],
          details: { model: result.model, decision, answers: result.answers, quota, settlement },
        };
      } catch (error: unknown) {
        return {
          content: [{ type: "text", text: `TypeSafe verifier unavailable: ${error instanceof Error ? error.message : String(error)}` }],
          details: { verdict: "unavailable" },
          isError: true,
        };
      }
    },
  });

  pi.registerCommand("typesafe-status", {
    description: "Show TypeSafe verifier mode and automatic-call budget without enabling network verification",
    handler: async (_args: string, ctx: unknown) => {
      const location = process.env.ORCA_PANE_KEY ? "Orca-launched OMP" : "direct OMP";
      const maxState: VerificationState = {
        request: "x".repeat(REQUEST_LIMIT),
        response: "x".repeat(RESPONSE_LIMIT),
        evidence: Array.from({ length: EVIDENCE_COUNT_LIMIT }, () => ({
          tool: "tool",
          text: "x".repeat(EVIDENCE_ITEM_LIMIT),
        })),
      };
      const maxCallCost = (estimatedInputTokens(maxState) / 1_000_000) * inputPrice;
      notify(
        ctx,
        `TypeSafe verifier: mode=${deps.mode}; surface=${location}; process_calls=${automaticCalls}/${callLimit}; daily_calls=${quotaOptions.dailyMaxCalls}; daily_budget_usd=${quotaOptions.dailyBudgetUsd.toFixed(2)}; max_estimated_call_usd=${maxCallCost.toFixed(6)}`,
        "info",
      );
    },
  });
}

export default function (pi: ExtensionApi): void {
  registerExtension(pi, {
    mode: verificationMode(),
    verify: verifyStateLive,
    maxAutomaticCalls: maxAutomaticCalls(),
    inputPricePerMillionUsd: inputPricePerMillionUsd(),
    quota: globalQuotaOptions(),
  });
}
