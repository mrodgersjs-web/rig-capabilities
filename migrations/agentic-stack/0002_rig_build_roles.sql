-- rig_build role isolation (Section IV). Cluster-wide roles: create once.
-- On Supabase, connect with a login role that is a MEMBER of exactly one of
-- these — never service_role/postgres, which bypass privileges as superuser
-- and would launder every denial below into a no-op.
-- Future migrations own their grants: re-GRANT any new table here explicitly;
-- no ALTER DEFAULT PRIVILEGES wildcard (deliberate: silence means denial).

DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rig_build_read') THEN
        CREATE ROLE rig_build_read NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rig_build_worker') THEN
        CREATE ROLE rig_build_worker NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rig_build_verifier') THEN
        CREATE ROLE rig_build_verifier NOLOGIN;
    END IF;
END $$;

REVOKE ALL ON SCHEMA rig_build FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA rig_build FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA rig_build FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA rig_build FROM PUBLIC;

GRANT USAGE ON SCHEMA rig_build TO rig_build_read, rig_build_worker, rig_build_verifier;

-- read: full visibility, nothing else
GRANT SELECT ON ALL TABLES IN SCHEMA rig_build TO rig_build_read;
GRANT rig_build_read TO rig_build_worker, rig_build_verifier;

-- worker: record attempts and events, advance outbox. No verdict, quality,
-- seal, or qualification surface; no UPDATE/DELETE anywhere (grants absent,
-- triggers refuse even the owner).
GRANT INSERT ON rig_build.trace TO rig_build_worker;
GRANT USAGE, SELECT ON SEQUENCE rig_build.trace_id_seq TO rig_build_worker;
GRANT INSERT ON rig_build.outbox TO rig_build_worker;
GRANT EXECUTE ON FUNCTION rig_build.record_trial(text, text, integer, text, text,
    text, text, text, text, jsonb, boolean, timestamptz, timestamptz) TO rig_build_worker;
GRANT EXECUTE ON FUNCTION rig_build.outbox_set_state(bigint, text, text) TO rig_build_worker;
GRANT EXECUTE ON FUNCTION rig_build.assess_quorum(text) TO rig_build_worker;

-- verifier: the only family allowed to record verdicts, scores, seals, and to
-- call qualification (which itself re-checks PASS-family + quorum in SQL).
GRANT INSERT ON rig_build.verdict, rig_build.quality_score, rig_build.seal_link
    TO rig_build_verifier;
GRANT USAGE, SELECT ON SEQUENCE rig_build.verdict_verdict_id_seq,
    rig_build.quality_score_score_id_seq TO rig_build_verifier;
GRANT EXECUTE ON FUNCTION rig_build.record_qualification(text, bigint)
    TO rig_build_verifier;
GRANT EXECUTE ON FUNCTION rig_build.assess_quorum(text) TO rig_build_verifier;
