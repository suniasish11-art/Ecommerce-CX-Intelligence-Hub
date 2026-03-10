-- ═══════════════════════════════════════════════════════════════
-- Ecommerce CX Intelligence Hub — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ═══════════════════════════════════════════════════════════════

-- ── 1. User Roles ────────────────────────────────────────────────
-- Extends Supabase Auth (auth.users is automatic)
CREATE TABLE IF NOT EXISTS user_roles (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role       TEXT NOT NULL CHECK (role IN ('viewer', 'manager', 'admin')),
    full_name  TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id)
);

-- ── 2. Tickets ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tickets (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id      TEXT UNIQUE NOT NULL,
    date           DATE,
    month          TEXT,
    category       TEXT,
    sub_issue      TEXT,
    status         TEXT,
    agent          TEXT,
    sentiment      TEXT,
    score          NUMERIC,
    revenue_impact NUMERIC,
    pattern_flag   TEXT,
    created_at     TIMESTAMPTZ DEFAULT now()
);

-- ── 3. Agent Performance ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_performance (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name   TEXT NOT NULL,
    team         TEXT,
    tickets      INTEGER,
    resolved     INTEGER,
    escalated    INTEGER,
    avg_score    NUMERIC,
    csat         NUMERIC,
    vs_target    NUMERIC,
    status       TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE(agent_name)
);

-- ── 4. Monthly Summary ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monthly_summary (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label      TEXT UNIQUE NOT NULL,
    total      INTEGER,
    loyalty    INTEGER,
    revenue    INTEGER,
    churn      INTEGER,
    resolved   INTEGER,
    pending    INTEGER,
    escalated  INTEGER,
    neg_pct    NUMERIC,
    avg_score  NUMERIC,
    avg_rev    NUMERIC,
    signals    INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ── 5. Enable Row Level Security on all tables ───────────────────
ALTER TABLE user_roles        ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets           ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summary   ENABLE ROW LEVEL SECURITY;

-- ── 6. RLS Policies ──────────────────────────────────────────────
-- Helper function: get current user's role
CREATE OR REPLACE FUNCTION get_my_role()
RETURNS TEXT AS $$
  SELECT role FROM user_roles WHERE user_id = auth.uid()
$$ LANGUAGE sql SECURITY DEFINER;

-- user_roles: users can read their own row only
CREATE POLICY "users_read_own_role"
  ON user_roles FOR SELECT
  USING (user_id = auth.uid());

-- tickets: viewer, manager, admin can all read
CREATE POLICY "tickets_read"
  ON tickets FOR SELECT
  USING (get_my_role() IN ('viewer', 'manager', 'admin'));

-- agent_performance: manager and admin only
CREATE POLICY "agents_read"
  ON agent_performance FOR SELECT
  USING (get_my_role() IN ('manager', 'admin'));

-- monthly_summary: viewer, manager, admin can all read
CREATE POLICY "monthly_read"
  ON monthly_summary FOR SELECT
  USING (get_my_role() IN ('viewer', 'manager', 'admin'));

-- ── 7. Indexes for performance ───────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tickets_category  ON tickets(category);
CREATE INDEX IF NOT EXISTS idx_tickets_status    ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_agent     ON tickets(agent);
CREATE INDEX IF NOT EXISTS idx_tickets_month     ON tickets(month);
CREATE INDEX IF NOT EXISTS idx_tickets_date      ON tickets(date);
