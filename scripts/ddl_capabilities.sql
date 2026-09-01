-- V14: capabilities schema for rig-dev-db (Supabase local). Idempotent.
CREATE SCHEMA IF NOT EXISTS capabilities;

CREATE TABLE IF NOT EXISTS capabilities.assets (
  id          text NOT NULL,
  kind        text NOT NULL,
  source      text NOT NULL,
  sha         text,
  description text,
  tags        jsonb DEFAULT '[]'::jsonb,
  okf         jsonb DEFAULT '{}'::jsonb,
  quality     jsonb DEFAULT '{}'::jsonb,
  lane        text,
  updated_at  timestamptz DEFAULT now(),
  PRIMARY KEY (id, kind, source)
);

CREATE TABLE IF NOT EXISTS capabilities.packs (
  id         text PRIMARY KEY,
  requester  text,
  intent     text,
  artifact   jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capabilities.ratings (
  pack    text,
  verdict text,
  ids     jsonb DEFAULT '[]'::jsonb,
  ts      timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capabilities.traces (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  text,
  event jsonb DEFAULT '{}'::jsonb,
  ts    timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capabilities.quality_runs (
  ts      timestamptz DEFAULT now(),
  asset   text,
  score   int,
  missing jsonb DEFAULT '[]'::jsonb
);

CREATE INDEX IF NOT EXISTS assets_lane_idx ON capabilities.assets (lane);
CREATE INDEX IF NOT EXISTS packs_requester_idx ON capabilities.packs (requester);
