-- rig_build operational schema — frozen contract v1 (Section IV, B06).
-- Independent of the capability-catalog mirror (scripts/ddl_capabilities.sql);
-- versioned migrations only, never rebuilt by catalog sync.
-- Quorum constants below are the frozen joint contract: n>=72 attempts keyed
-- by (cell, trial_id, attempt_seq), durable-arm >=10, 24h spread. Statistics
-- (Wilson lower bound per measurement-rules-v1) stay in measure.py; SQL only
-- enforces quorum presence, never recomputes confidence.

CREATE SCHEMA IF NOT EXISTS rig_build;

CREATE TABLE rig_build.trial (
    cell            text        NOT NULL,
    trial_id        text        NOT NULL,
    attempt_seq     integer     NOT NULL CHECK (attempt_seq >= 1),
    family          text        NOT NULL CHECK (family <> ''),
    model           text        NOT NULL CHECK (model <> ''),
    node            text        NOT NULL CHECK (node <> ''),
    task_sha        text        NOT NULL CHECK (task_sha ~ '^[0-9a-f]{64}$'),
    outcome         text        NOT NULL CHECK (outcome IN
                          ('pass','fail','error','timeout','blocked')),
    artifact_tree   text        CHECK (artifact_tree IS NULL OR artifact_tree ~ '^[0-9a-f]{40,64}$'),
    evidence        jsonb       NOT NULL DEFAULT '{}'::jsonb,
    durable         boolean     NOT NULL DEFAULT false,
    started_at      timestamptz NOT NULL,
    finished_at     timestamptz NOT NULL,
    recorded_by     text        NOT NULL DEFAULT current_user,
    recorded_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (cell, trial_id, attempt_seq),
    CHECK (finished_at >= started_at)
);

-- Append-only run events. Updates and deletes are refused by trigger even for
-- the table owner; roles in 0002 never receive UPDATE/DELETE in the first place.
CREATE TABLE rig_build.trace (
    id          bigserial   PRIMARY KEY,
    cell        text        NOT NULL,
    trial_id    text        NOT NULL,
    seq         integer     NOT NULL CHECK (seq >= 1),
    event       text        NOT NULL CHECK (event <> ''),
    payload     jsonb       NOT NULL DEFAULT '{}'::jsonb,
    at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (cell, trial_id, seq)
);

CREATE TABLE rig_build.verdict (
    verdict_id        bigserial   PRIMARY KEY,
    cell              text        NOT NULL,
    family            text        NOT NULL CHECK (family <> ''),
    verdict           text        NOT NULL CHECK (verdict IN
                          ('PERFECT','VERIFIED','PARTIAL','FEEDBACK','FAILED')),
    candidate_commit  text        NOT NULL CHECK (candidate_commit ~ '^[0-9a-f]{40,64}$'),
    candidate_tree    text        NOT NULL CHECK (candidate_tree ~ '^[0-9a-f]{40,64}$'),
    findings          jsonb       NOT NULL DEFAULT '[]'::jsonb,
    verdict_at        timestamptz NOT NULL,
    recorded_by       text        NOT NULL DEFAULT current_user,
    recorded_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE rig_build.quality_score (
    score_id    bigserial   PRIMARY KEY,
    cell        text        NOT NULL,
    trial_id    text        NOT NULL,
    attempt_seq integer     NOT NULL,
    rubric      text        NOT NULL CHECK (rubric <> ''),
    score       numeric     NOT NULL CHECK (score >= 0 AND score <= 100),
    checks      jsonb       NOT NULL DEFAULT '{}'::jsonb,
    recorded_by text        NOT NULL DEFAULT current_user,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (cell, trial_id, attempt_seq)
        REFERENCES rig_build.trial (cell, trial_id, attempt_seq)
);

CREATE TABLE rig_build.seal_link (
    packet_hash   text        NOT NULL CHECK (packet_hash ~ '^[0-9a-f]{64}$'),
    target_table  text        NOT NULL CHECK (target_table IN
                      ('trial','trace','verdict','quality_score')),
    target_key    text        NOT NULL,
    sealed_by     text        NOT NULL DEFAULT current_user,
    sealed_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (packet_hash, target_table, target_key)
);

-- Outbox: ambiguous provider acknowledgment becomes an explicit 'unknown'
-- reconciliation state. Automatic resend from 'unknown' does not exist;
-- only the state-machine function (below) may change state.
CREATE TABLE rig_build.outbox (
    outbox_id    bigserial   PRIMARY KEY,
    topic        text        NOT NULL CHECK (topic <> ''),
    payload      jsonb       NOT NULL,
    state        text        NOT NULL DEFAULT 'pending' CHECK (state IN
                   ('pending','sent','unknown','reconciled')),
    attempts     integer     NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    last_change  timestamptz NOT NULL DEFAULT now(),
    note         text        NOT NULL DEFAULT ''
);

-- qualification is derived, never hand-written: only record_qualification()
-- inserts, and only from a PASS-family verdict over a quorum-bearing cell.
CREATE TABLE rig_build.qualification (
    cell        text        PRIMARY KEY,
    verdict_id  bigint      NOT NULL REFERENCES rig_build.verdict (verdict_id),
    n_attempts  integer     NOT NULL,
    n_durable   integer     NOT NULL,
    span_hours  numeric     NOT NULL,
    assessed_at timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION rig_build._append_only() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'rig_build.% is append-only', TG_TABLE_NAME;
END $$;

CREATE TRIGGER trace_append_only BEFORE UPDATE OR DELETE ON rig_build.trace
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();
CREATE TRIGGER seal_append_only BEFORE UPDATE OR DELETE ON rig_build.seal_link
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();
CREATE TRIGGER qualification_append_only BEFORE UPDATE OR DELETE ON rig_build.qualification
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();

-- Direct row edits are refused for every role including the owner; the named
-- functions below are the only writers, and each validates its own predicate.
CREATE FUNCTION rig_build._no_direct_write() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF current_setting('rig_build.in_named_fn', true) IS DISTINCT FROM 'on' THEN
        RAISE EXCEPTION 'rig_build.%: writes only through named functions', TG_TABLE_NAME;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER outbox_named_fn BEFORE UPDATE ON rig_build.outbox
    FOR EACH ROW EXECUTE FUNCTION rig_build._no_direct_write();
CREATE TRIGGER trial_named_fn BEFORE INSERT OR UPDATE ON rig_build.trial
    FOR EACH ROW EXECUTE FUNCTION rig_build._no_direct_write();

CREATE TRIGGER trial_append_only BEFORE UPDATE OR DELETE ON rig_build.trial
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();
CREATE TRIGGER verdict_append_only BEFORE UPDATE OR DELETE ON rig_build.verdict
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();
CREATE TRIGGER quality_append_only BEFORE UPDATE OR DELETE ON rig_build.quality_score
    FOR EACH ROW EXECUTE FUNCTION rig_build._append_only();

-- Named trial writer (SECURITY INVOKER: recorded_by stays honest).
CREATE FUNCTION rig_build.record_trial(p_cell text, p_trial_id text, p_attempt_seq integer,
        p_family text, p_model text, p_node text, p_task_sha text, p_outcome text,
        p_artifact_tree text, p_evidence jsonb, p_durable boolean,
        p_started_at timestamptz, p_finished_at timestamptz)
RETURNS rig_build.trial LANGUAGE plpgsql SECURITY INVOKER
SET search_path = rig_build, public AS $$
DECLARE row rig_build.trial;
BEGIN
    PERFORM set_config('rig_build.in_named_fn', 'on', true);
    INSERT INTO rig_build.trial (cell, trial_id, attempt_seq, family, model, node,
        task_sha, outcome, artifact_tree, evidence, durable, started_at, finished_at)
    VALUES (p_cell, p_trial_id, p_attempt_seq, p_family, p_model, p_node,
        p_task_sha, p_outcome, p_artifact_tree,
        COALESCE(p_evidence, '{}'::jsonb), p_durable, p_started_at, p_finished_at)
    RETURNING * INTO row;
    PERFORM set_config('rig_build.in_named_fn', 'off', true);
    RETURN row;
END $$;
REVOKE EXECUTE ON FUNCTION rig_build.record_trial(text, text, integer, text, text, text,
    text, text, text, jsonb, boolean, timestamptz, timestamptz) FROM PUBLIC;
-- State machine: pending -> sent|unknown; sent -> reconciled|unknown;
-- unknown -> reconciled (evidence in note) or back to pending (attempts+1).
CREATE FUNCTION rig_build.outbox_set_state(p_outbox_id bigint, p_next text,
                                           p_note text DEFAULT '')
RETURNS rig_build.outbox LANGUAGE plpgsql SECURITY DEFINER SET search_path = rig_build, public AS $$
DECLARE
    row rig_build.outbox;
    legal boolean;
BEGIN
    SELECT * INTO row FROM rig_build.outbox WHERE outbox_id = p_outbox_id
        FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'outbox % not found', p_outbox_id;
    END IF;
    legal := CASE
        WHEN row.state = 'pending' AND p_next IN ('sent','unknown') THEN true
        WHEN row.state = 'sent'    AND p_next IN ('reconciled','unknown') THEN true
        WHEN row.state = 'unknown' AND p_next IN ('reconciled','pending') THEN true
        ELSE false
    END;
    IF NOT legal THEN
        RAISE EXCEPTION 'illegal outbox transition % -> %', row.state, p_next;
    END IF;
    IF p_next = 'unknown' AND p_note = '' THEN
        RAISE EXCEPTION 'unknown requires reconciliation note';
    END IF;
    PERFORM set_config('rig_build.in_named_fn', 'on', true);
    UPDATE rig_build.outbox
       SET state = p_next,
           attempts = attempts + CASE WHEN p_next = 'pending' THEN 1 ELSE 0 END,
           last_change = now(),
           note = p_note
     WHERE outbox_id = p_outbox_id;
    PERFORM set_config('rig_build.in_named_fn', 'off', true);
    SELECT * INTO row FROM rig_build.outbox WHERE outbox_id = p_outbox_id;
    RETURN row;
END $$;

-- Frozen joint contract constants (see header). Statistics live in measure.py.
CREATE FUNCTION rig_build.assess_quorum(p_cell text)
RETURNS TABLE (n_attempts bigint, n_durable bigint, span_hours numeric)
LANGUAGE sql STABLE AS $$
    SELECT count(*),
           count(*) FILTER (WHERE durable),
           COALESCE(EXTRACT(EPOCH FROM (max(finished_at) - min(finished_at))) / 3600.0, 0)::numeric(12,3)
      FROM rig_build.trial
     WHERE cell = p_cell
$$;

CREATE FUNCTION rig_build.record_qualification(p_cell text, p_verdict_id bigint)
RETURNS rig_build.qualification
LANGUAGE plpgsql SECURITY DEFINER SET search_path = rig_build, public AS $$
DECLARE
    v rig_build.verdict;
    q record;
    row rig_build.qualification;
BEGIN
    SELECT * INTO v FROM rig_build.verdict WHERE verdict_id = p_verdict_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'verdict % not found', p_verdict_id;
    END IF;
    IF v.verdict NOT IN ('PERFECT','VERIFIED') THEN
        RAISE EXCEPTION 'qualification requires PERFECT|VERIFIED, got %', v.verdict;
    END IF;
    IF v.cell <> p_cell THEN
        RAISE EXCEPTION 'verdict % belongs to cell %, not %', p_verdict_id, v.cell, p_cell;
    END IF;
    SELECT * INTO q FROM rig_build.assess_quorum(p_cell);
    IF q.n_attempts < 72 THEN
        RAISE EXCEPTION 'quorum n=% < 72 attempts', q.n_attempts;
    END IF;
    IF q.n_durable < 10 THEN
        RAISE EXCEPTION 'durable-arm % < 10', q.n_durable;
    END IF;
    IF q.span_hours < 24 THEN
        RAISE EXCEPTION 'spread %h < 24h', q.span_hours;
    END IF;
    PERFORM set_config('rig_build.in_named_fn', 'on', true);
    INSERT INTO rig_build.qualification (cell, verdict_id, n_attempts, n_durable, span_hours)
    VALUES (p_cell, p_verdict_id, q.n_attempts, q.n_durable, q.span_hours)
    RETURNING * INTO row;
    PERFORM set_config('rig_build.in_named_fn', 'off', true);
    RETURN row;
END $$;

REVOKE EXECUTE ON FUNCTION rig_build.outbox_set_state(bigint, text, text) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION rig_build.record_qualification(text, bigint) FROM PUBLIC;
