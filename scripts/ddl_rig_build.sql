-- ============================================================================
-- rig_build — private operational schema for the durable build backend
-- (Durable Setup & Repeatable Results plan, Section IV: B03–B06 frozen
-- contract; B14–B19 entities). Independent of the capability-catalog mirror
-- (scripts/ddl_capabilities.sql).
--
-- MIGRATION PROCEDURE (B06/B12/B13):
--   1. python3 rig_capabilities/build_migrate.py plan
--      -> prints/writes the plan receipt (DDL sha256, entity inventory).
--   2. python3 rig_capabilities/build_migrate.py apply --dsn "$RIG_CAP_DSN" \
--          --confirm rig_build_v1_apply
--      apply refuses without the exact token, proves target identity FIRST
--      (select current_database(), current_user), and echoes the probe plus
--      the DDL sha into a receipt under
--      runs/agentic-stack-buildout/backend/. Nothing applies automatically.
--      This file is versioned-migration material (B13): it is applied ONCE per
--      target through build_migrate, never re-derived from a sync job.
--   3. python3 rig_capabilities/build_migrate.py verify --dsn "$RIG_CAP_DSN"
--      re-reads schema/table/constraint/trigger/role presence from the live
--      catalog; a PASS is a fresh catalog read, never a stored receipt.
--
-- ROLLBACK: the ROLLBACK section at the foot of this file is the exact reverse
--   (drop triggers -> policies -> grants/roles -> tables -> schema, reverse
--   dependency order). build_migrate extracts and prints it with
--   `plan`/`rollback-plan`; it is executed by a human or through the
--   --confirm discipline, never by the apply path. Data in this schema is
--   run state: rollback DESTROYS run history. Prefer forward migration.
--
-- CATALOG-SYNC LAW: rig_capabilities/sync.py (ddl_capabilities.sql, the
--   capabilities.* mirror) MUST NEVER truncate, drop, or recreate anything in
--   rig_build. Run state is append-authoritative; the catalog mirror is a
--   rebuildable projection. The two schemas share no tables and no grants.
--
-- IDENTITY: rig_build_data_plane  — workers/MCP: SELECT/INSERT + narrow
--   EXECUTE-UPDATE (runs state, outbox claim/settle). NEVER UPDATE/DELETE on
--   run_events, cell_contracts, process_versions, approval_refs.
--   rig_build_operator — reconciliation + readback; still cannot UPDATE
--   append-only tables (the DB says so, not the code path).
--   Neither role may mint approval or qualification: approval_refs stores
--   REFERENCES to the authoritative gate-d ledger only; no column in this
--   schema can hold an approved/qualified PASS minted from a data-plane write.
-- ============================================================================

-- >>>> APPLY-PORTABLE-BEGIN (Postgres executes verbatim; the offline sqlite
--      structural harness in tests/test_build_store.py executes this section
--      with only the CREATE SCHEMA line removed — documented adaptation)
CREATE SCHEMA IF NOT EXISTS rig_build;

-- B14 — frozen cell criteria: one contract per (cell, criteria version).
-- Immutability is enforced by the PG-only guard below and by the store
-- (a differing rewrite is refused; a byte-identical replay is a no-op).
CREATE TABLE IF NOT EXISTS rig_build.cell_contracts (
    cell_id             text        NOT NULL CHECK (cell_id <> ''),
    criteria_version    text        NOT NULL CHECK (criteria_version <> ''),
    contract            jsonb       NOT NULL DEFAULT '{}',
    contract_sha256     text        NOT NULL CHECK (length(contract_sha256) = 64),
    criteria_pack_sha256 text       NOT NULL CHECK (length(criteria_pack_sha256) = 64),
    sealed_by           text        NOT NULL CHECK (sealed_by <> ''),
    sealed_at           timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cell_id, criteria_version)
);

-- B14 — immutable process versions: the frozen worker/process contract
-- (identity, cadence, envelope). Any change is a NEW version row.
CREATE TABLE IF NOT EXISTS rig_build.process_versions (
    process_key         text        NOT NULL CHECK (process_key <> ''),
    version             text        NOT NULL CHECK (version <> ''),
    definition          jsonb       NOT NULL DEFAULT '{}',
    definition_sha256   text        NOT NULL CHECK (length(definition_sha256) = 64),
    declared_owner      text        NOT NULL CHECK (declared_owner <> ''),
    resource_envelope   jsonb       NOT NULL DEFAULT '{}',
    registered_by       text        NOT NULL CHECK (registered_by <> ''),
    registered_at       timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (process_key, version)
);

-- B14 — cell bindings: which frozen process-version owns a cell contract,
-- with the T1–T8 work-type and the owner selected from the authority
-- (authority/standards/tool_selection.v2.json via tool_selection.py);
-- the binding records the choice, it cannot choose a default.
CREATE TABLE IF NOT EXISTS rig_build.cell_bindings (
    cell_id             text        NOT NULL,
    criteria_version    text        NOT NULL,
    process_key         text        NOT NULL,
    process_version     text        NOT NULL,
    work_type           text        NOT NULL CHECK (work_type IN
                              ('T1','T2','T3','T4','T5','T6','T7','T8')),
    owner               text        NOT NULL CHECK (owner <> ''),
    facts               jsonb       NOT NULL DEFAULT '{}',
    bound_by            text        NOT NULL CHECK (bound_by <> ''),
    bound_at            timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cell_id, criteria_version, process_key, process_version),
    FOREIGN KEY (cell_id, criteria_version)
        REFERENCES rig_build.cell_contracts (cell_id, criteria_version),
    FOREIGN KEY (process_key, process_version)
        REFERENCES rig_build.process_versions (process_key, version)
);

-- B15 — run registry. The idempotency key is the ONLY replay handle: a
-- duplicate key returns the existing run, it never forks a second one.
-- fencing_token only ever increases (trigger, PG-only); a writer whose token
-- is below the stored value is stale and its commits are refused.
-- `succeeded` records an OBSERVED outcome after verification elsewhere —
-- no column here accepts a caller-minted qualification.
CREATE TABLE IF NOT EXISTS rig_build.runs (
    run_id              text        NOT NULL PRIMARY KEY,
    idempotency_key     text        NOT NULL UNIQUE,
    cell_id             text        NOT NULL,
    criteria_version    text        NOT NULL,
    process_key         text        NOT NULL,
    process_version     text        NOT NULL,
    state               text        NOT NULL CHECK (state IN
                              ('requested','running','waiting_approval',
                               'blocked','succeeded','failed','cancelled')),
    fencing_token       bigint      NOT NULL DEFAULT 1 CHECK (fencing_token >= 1),
    started_by          text        NOT NULL CHECK (started_by <> ''),
    started_at          timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checkpoint          jsonb       NOT NULL DEFAULT '{}',
    FOREIGN KEY (cell_id, criteria_version)
        REFERENCES rig_build.cell_contracts (cell_id, criteria_version),
    FOREIGN KEY (process_key, process_version)
        REFERENCES rig_build.process_versions (process_key, version)
);
CREATE INDEX IF NOT EXISTS runs_state_idx ON rig_build.runs (state);

-- B15 — append-only transition/checkpoint events. Primary key
-- (run_id, sequence): duplicates are a key violation in every engine.
-- Sequence continuity (exactly max+1) is guarded by the PG-only trigger and
-- enforced again in build_store.append_event. UPDATE/DELETE are refused by
-- trigger (below) AND never granted to the data-plane role (grants, below).
CREATE TABLE IF NOT EXISTS rig_build.run_events (
    run_id              text        NOT NULL
                              REFERENCES rig_build.runs (run_id),
    sequence            integer     NOT NULL CHECK (sequence >= 1),
    kind                text        NOT NULL CHECK (kind IN
                              ('transition','checkpoint','receipt','note')),
    payload             jsonb       NOT NULL DEFAULT '{}',
    fencing_token       bigint      NOT NULL CHECK (fencing_token >= 1),
    occurred_at         timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, sequence)
);

-- B16 — content-addressed artifacts. The content hash is the identity: the
-- store recomputes it from bytes before insert and refuses on mismatch
-- (build_store.add_artifact); the unique key makes re-registration a no-op.
CREATE TABLE IF NOT EXISTS rig_build.artifacts (
    content_sha256      text        NOT NULL CHECK (length(content_sha256) = 64),
    uri                 text        NOT NULL CHECK (uri <> ''),
    run_id              text        NOT NULL
                              REFERENCES rig_build.runs (run_id),
    kind                text        NOT NULL CHECK (kind <> ''),
    size_bytes          bigint      NOT NULL CHECK (size_bytes >= 0),
    recorded_by         text        NOT NULL CHECK (recorded_by <> ''),
    recorded_at         timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (content_sha256, uri)
);
CREATE INDEX IF NOT EXISTS artifacts_run_idx ON rig_build.artifacts (run_id);

-- B17 — approval REFERENCES only. This table stores a pointer into the
-- authoritative approval ledger (gate-d) plus its external ref; it has no
-- status/verdict column, so it cannot hold — let alone mint — consent.
-- Approval validation lives in gate_d/commit_gate and is NOT duplicated or
-- weakened here. (authority_ledger = 'self' is refused: self-approval has no
-- external ref to point at.)
CREATE TABLE IF NOT EXISTS rig_build.approval_refs (
    authority_ledger    text        NOT NULL CHECK (authority_ledger <> ''
                              AND lower(authority_ledger) <> 'self'),
    external_ref        text        NOT NULL CHECK (external_ref <> ''),
    subject_kind        text        NOT NULL CHECK (subject_kind IN
                              ('run','cell_omission','build')),
    subject_id          text        NOT NULL CHECK (subject_id <> ''),
    requested_by        text        NOT NULL CHECK (requested_by <> ''),
    recorded_by         text        NOT NULL CHECK (recorded_by <> ''),
    recorded_at         timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (authority_ledger, external_ref),
    CHECK (subject_kind <> 'run' OR external_ref NOT LIKE 'caller:%')
);

-- B18 — resumable source-document/intel ingestion state. dedupe_key (sha256
-- over the canonicalized source identity) is unique: a re-accepted source is
-- the SAME row, never a second accepted copy. retrieval_status records every
-- terminal outcome; a missing/truncated caption is a recorded GAP, never a
-- silently skipped source. A FETCHED row must carry its content hash.
CREATE TABLE IF NOT EXISTS rig_build.source_documents (
    dedupe_key          text        PRIMARY KEY CHECK (length(dedupe_key) = 64),
    url                 text        NOT NULL CHECK (url LIKE 'https://%'),
    provider            text        NOT NULL CHECK (provider <> ''),
    kind                text        NOT NULL CHECK (kind <> ''),
    retrieval_status    text        NOT NULL CHECK (retrieval_status IN
                              ('PENDING','FETCHING','FETCHED','TRUNCATED',
                               'MISSING','FAILED','REPLACED')),
    content_sha256      text        CHECK (content_sha256 IS NULL
                              OR length(content_sha256) = 64),
    raw_sha256          text        CHECK (raw_sha256 IS NULL
                              OR length(raw_sha256) = 64),
    expected_artifact   text        NOT NULL DEFAULT '',
    why_version_applicable text     NOT NULL DEFAULT '',
    attempt_count       integer     NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_error          text,
    updated_at          timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (retrieval_status <> 'FETCHED' OR content_sha256 IS NOT NULL)
);

-- B19 — transactional outbox with claim lease + fencing. Delivery states:
-- pending -> claimed -> (sent | failed | unknown). `unknown` is the honest
-- state for an ambiguous remote acknowledgment; it is ONLY terminal after
-- build_store.reconcile_unknown, which requires named evidence — a blind
-- resend is refused by construction (settle cannot emit pending from
-- claimed; reconcile cannot clear unknown without an evidence string).
CREATE TABLE IF NOT EXISTS rig_build.outbox (
    outbox_id           text        NOT NULL PRIMARY KEY,
    topic               text        NOT NULL CHECK (topic <> ''),
    payload             jsonb       NOT NULL DEFAULT '{}',
    state               text        NOT NULL DEFAULT 'pending' CHECK (state IN
                              ('pending','claimed','sent','failed','unknown')),
    claim_owner         text,
    claim_fence         bigint      NOT NULL DEFAULT 0 CHECK (claim_fence >= 0),
    lease_expires_at    timestamptz,
    attempt_count       integer     NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    last_error          text,
    created_at          timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (state <> 'claimed' OR claim_owner IS NOT NULL),
    CHECK (state = 'claimed' OR lease_expires_at IS NULL
                              OR lease_expires_at < updated_at)
);
CREATE INDEX IF NOT EXISTS outbox_claim_idx ON rig_build.outbox (state, lease_expires_at);
-- <<<< APPLY-PORTABLE-END

-- >>>> APPLY-PGONLY-BEGIN (roles, grants, RLS, append-only guards; stripped
--      by the offline sqlite harness — these invariants are listed as
--      BLOCKED/needs-live-proof in tests/test_build_store.py, not pretended
--      to be sqlite-proven)

-- Roles are created only if absent (idempotent re-apply). No passwords:
-- credentials are connection-level, provisioned by the scoped-credential
-- approval step (B11/B12), never by this file.
DO $pg$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rig_build_data_plane') THEN
    CREATE ROLE rig_build_data_plane NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rig_build_operator') THEN
    CREATE ROLE rig_build_operator NOLOGIN;
  END IF;
END $pg$;

GRANT USAGE ON SCHEMA rig_build TO rig_build_data_plane, rig_build_operator;

-- Data plane: reads + appends + the two narrow claim/update verbs.
GRANT SELECT ON ALL TABLES IN SCHEMA rig_build TO rig_build_data_plane;
GRANT INSERT ON rig_build.cell_contracts, rig_build.process_versions,
                rig_build.cell_bindings, rig_build.runs, rig_build.run_events,
                rig_build.artifacts, rig_build.approval_refs,
                rig_build.source_documents, rig_build.outbox
     TO rig_build_data_plane;
GRANT UPDATE (state, fencing_token, updated_at, checkpoint) ON rig_build.runs
     TO rig_build_data_plane;
GRANT UPDATE (state, claim_owner, claim_fence, lease_expires_at,
              attempt_count, last_error, updated_at) ON rig_build.outbox
     TO rig_build_data_plane;
-- Data plane holds NO update on run_events / approval_refs / the frozen
-- record tables, and NO delete anywhere in rig_build.

-- Operator: full read, reconciliation updates on outbox/runs only, plus
-- source-document state moves for resume. Append-only tables stay append-only.
GRANT SELECT ON ALL TABLES IN SCHEMA rig_build TO rig_build_operator;
GRANT UPDATE ON rig_build.runs, rig_build.outbox, rig_build.source_documents
     TO rig_build_operator;

-- Append-only guards. RAISE EXCEPTION fires for every role, including the
-- table owner — code-path discipline plus database law.
CREATE OR REPLACE FUNCTION rig_build.refuse_mutation() RETURNS trigger
LANGUAGE plpgsql AS $fn$
BEGIN
  RAISE EXCEPTION 'rig_build.% is append-only: % refused', TG_TABLE_NAME, TG_OP;
END $fn$;

DROP TRIGGER IF EXISTS run_events_append_only ON rig_build.run_events;
CREATE TRIGGER run_events_append_only
    BEFORE UPDATE OR DELETE ON rig_build.run_events
    FOR EACH ROW EXECUTE FUNCTION rig_build.refuse_mutation();

-- sequence continuity: NEW.sequence must be exactly MAX+1 for its run.
CREATE OR REPLACE FUNCTION rig_build.require_next_sequence() RETURNS trigger
LANGUAGE plpgsql AS $fn$
BEGIN
  IF NEW.sequence <> COALESCE((SELECT MAX(sequence) FROM rig_build.run_events
                               WHERE run_id = NEW.run_id), 0) + 1 THEN
    RAISE EXCEPTION 'run_events sequence must be max+1 for run % (got %)',
        NEW.run_id, NEW.sequence;
  END IF;
  RETURN NEW;
END $fn$;

DROP TRIGGER IF EXISTS run_events_next_sequence ON rig_build.run_events;
CREATE TRIGGER run_events_next_sequence
    BEFORE INSERT ON rig_build.run_events
    FOR EACH ROW EXECUTE FUNCTION rig_build.require_next_sequence();

-- frozen-record guards: criteria contracts and process versions are immutable
-- once sealed (a correction is a new version row, never an overwrite).
DROP TRIGGER IF EXISTS cell_contracts_immutable ON rig_build.cell_contracts;
CREATE TRIGGER cell_contracts_immutable
    BEFORE UPDATE OR DELETE ON rig_build.cell_contracts
    FOR EACH ROW EXECUTE FUNCTION rig_build.refuse_mutation();

DROP TRIGGER IF EXISTS process_versions_immutable ON rig_build.process_versions;
CREATE TRIGGER process_versions_immutable
    BEFORE UPDATE OR DELETE ON rig_build.process_versions
    FOR EACH ROW EXECUTE FUNCTION rig_build.refuse_mutation();

-- approval refs are write-once references (a revocation is a NEW ref row
-- pointing at the ledger's revocation record, never an edit).
DROP TRIGGER IF EXISTS approval_refs_immutable ON rig_build.approval_refs;
CREATE TRIGGER approval_refs_immutable
    BEFORE UPDATE OR DELETE ON rig_build.approval_refs
    FOR EACH ROW EXECUTE FUNCTION rig_build.refuse_mutation();

-- fencing monotonicity: a commit may never LOWER a run's fencing token; the
-- only legal change is +1 on an explicit takeover.
CREATE OR REPLACE FUNCTION rig_build.require_fencing_advance() RETURNS trigger
LANGUAGE plpgsql AS $fn$
BEGIN
  IF NEW.fencing_token < OLD.fencing_token THEN
    RAISE EXCEPTION 'fencing token may not decrease (old % new %)',
        OLD.fencing_token, NEW.fencing_token;
  END IF;
  RETURN NEW;
END $fn$;

DROP TRIGGER IF EXISTS runs_fencing_monotonic ON rig_build.runs;
CREATE TRIGGER runs_fencing_monotonic
    BEFORE UPDATE OF fencing_token ON rig_build.runs
    FOR EACH ROW EXECUTE FUNCTION rig_build.require_fencing_advance();

-- B20 — RLS: the operational schema is unexposed by default. Policies exist
-- for the two rig_build roles only; no anonymous/authenticated access is
-- granted, so PostgREST/API surface exposure is structurally impossible
-- unless an explicit reviewed contract adds it later.
ALTER TABLE rig_build.runs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig_build.run_events   ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig_build.artifacts    ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig_build.outbox       ENABLE ROW LEVEL SECURITY;
ALTER TABLE rig_build.approval_refs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS dp_read ON rig_build.runs;
CREATE POLICY dp_read ON rig_build.runs
    FOR SELECT TO rig_build_data_plane, rig_build_operator USING (true);
DROP POLICY IF EXISTS dp_write ON rig_build.runs;
CREATE POLICY dp_write ON rig_build.runs
    FOR INSERT TO rig_build_data_plane WITH CHECK (true);
DROP POLICY IF EXISTS dp_update ON rig_build.runs;
CREATE POLICY dp_update ON rig_build.runs
    FOR UPDATE TO rig_build_data_plane USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS dp_rw ON rig_build.run_events;
CREATE POLICY dp_rw ON rig_build.run_events
    FOR ALL TO rig_build_data_plane, rig_build_operator
    USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS dp_rw ON rig_build.artifacts;
CREATE POLICY dp_rw ON rig_build.artifacts
    FOR ALL TO rig_build_data_plane, rig_build_operator
    USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS dp_rw ON rig_build.outbox;
CREATE POLICY dp_rw ON rig_build.outbox
    FOR ALL TO rig_build_data_plane, rig_build_operator
    USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS dp_rw ON rig_build.approval_refs;
CREATE POLICY dp_rw ON rig_build.approval_refs
    FOR ALL TO rig_build_data_plane, rig_build_operator
    USING (true) WITH CHECK (true);
-- <<<< APPLY-PGONLY-END

-- >>>> ROLLBACK-BEGIN (reverse dependency order; NEVER run by the apply path;
--      DESTROYS run state — see header; extract with build_migrate.py)
-- DROP TRIGGER IF EXISTS runs_fencing_monotonic       ON rig_build.runs;
-- DROP FUNCTION IF EXISTS rig_build.require_fencing_advance();
-- DROP TRIGGER IF EXISTS approval_refs_immutable      ON rig_build.approval_refs;
-- DROP TRIGGER IF EXISTS process_versions_immutable   ON rig_build.process_versions;
-- DROP TRIGGER IF EXISTS cell_contracts_immutable     ON rig_build.cell_contracts;
-- DROP TRIGGER IF EXISTS run_events_next_sequence     ON rig_build.run_events;
-- DROP TRIGGER IF EXISTS run_events_append_only       ON rig_build.run_events;
-- DROP FUNCTION IF EXISTS rig_build.require_next_sequence();
-- DROP FUNCTION IF EXISTS rig_build.refuse_mutation();
-- DROP POLICY IF EXISTS dp_update ON rig_build.runs;
-- DROP POLICY IF EXISTS dp_write  ON rig_build.runs;
-- DROP POLICY IF EXISTS dp_read   ON rig_build.runs;
-- DROP POLICY IF EXISTS dp_rw ON rig_build.approval_refs;
-- DROP POLICY IF EXISTS dp_rw ON rig_build.outbox;
-- DROP POLICY IF EXISTS dp_rw ON rig_build.artifacts;
-- DROP POLICY IF EXISTS dp_rw ON rig_build.run_events;
-- DROP TABLE IF EXISTS rig_build.outbox;
-- DROP TABLE IF EXISTS rig_build.source_documents;
-- DROP TABLE IF EXISTS rig_build.approval_refs;
-- DROP TABLE IF EXISTS rig_build.artifacts;
-- DROP TABLE IF EXISTS rig_build.run_events;
-- DROP TABLE IF EXISTS rig_build.runs;
-- DROP TABLE IF EXISTS rig_build.cell_bindings;
-- DROP TABLE IF EXISTS rig_build.process_versions;
-- DROP TABLE IF EXISTS rig_build.cell_contracts;
-- DROP SCHEMA IF EXISTS rig_build;
-- (roles are left in place: revoking membership + a human drop is a
--  credential-scope decision per B11, not a schema rollback.)
-- <<<< ROLLBACK-END
