/**
 * arifOS Supabase TypeScript Client
 *
 * Replaces all /root/... and /tmp/... JSON state writes with Postgres calls.
 * For use in A-FORGE TypeScript runtime (Node.js / NodeNext).
 *
 * Usage:
 *   import { createSupabaseClient, sealVault, openSession } from './supabase_client.ts';
 *
 * Environment variables:
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let _client: SupabaseClient | null = null;

export function createSupabaseClient(): SupabaseClient {
  if (_client) return _client;

  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  }

  _client = createClient(url, key, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });

  return _client;
}

// ── VAULT999 ──────────────────────────────────────────────────────────────────

export async function sealVault(record: {
  sealId: string;
  sessionId: string;
  verdict: "SEAL" | "HOLD" | "SABAR" | "VOID";
  timestamp: string;
  recordId?: string;
  prevHash?: string;
  hashofinput?: string;
  telemetrysnapshot?: Record<string, number>;
  floorsTriggered?: string[];
  irreversibilityacknowledged?: boolean;
  task?: string;
  finalText?: string;
  turnCount?: number;
  profileName?: string;
  escalation?: Record<string, unknown>;
  data?: Record<string, unknown>;
}): Promise<void> {
  const sb = createSupabaseClient();

  const payload = {
    seal_id: record.sealId,
    session_id: record.sessionId,
    verdict: record.verdict,
    timestamp: record.timestamp,
    record_id: record.recordId,
    prev_hash: record.prevHash,
    hashofinput: record.hashofinput,
    telemetrysnapshot: record.telemetrysnapshot ?? null,
    floors_triggered: record.floorsTriggered ?? [],
    irreversibilityacknowledged: record.irreversibilityacknowledged ?? false,
    task: record.task ?? null,
    final_text: record.finalText ?? null,
    turn_count: record.turnCount ?? 0,
    profile_name: record.profileName ?? null,
    escalation: record.escalation ?? null,
  };

  const fullData = record.data ?? payload;

  const { error } = await sb
    .from("arifosmcp_vault_seals")
    .insert({
      ...payload,
      data: fullData,
    });

  if (error) throw error;
  console.error(`[arifOS] SEAL written: ${record.sealId} verdict=${record.verdict}`);
}

export async function queryVaultSeals(options?: {
  sessionId?: string;
  verdict?: string;
  since?: string;
  until?: string;
  limit?: number;
}): Promise<Record<string, unknown>[]> {
  const sb = createSupabaseClient();
  let q = sb
    .from("arifosmcp_vault_seals")
    .select("*")
    .order("timestamp", { ascending: false });

  if (options?.sessionId) q = q.eq("session_id", options.sessionId);
  if (options?.verdict) q = q.eq("verdict", options.verdict);
  if (options?.since) q = q.gte("timestamp", options.since);
  if (options?.until) q = q.lte("timestamp", options.until);
  if (options?.limit) q = q.limit(options.limit);

  const { data, error } = await q;
  if (error) throw error;
  return data ?? [];
}

// ── SESSIONS ──────────────────────────────────────────────────────────────────

export async function openSession(params: {
  sessionId: string;
  agentId: string;
  riskTier?: string;
  declaredIntent?: string;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb
    .from("arifosmcp_sessions")
    .upsert(
      {
        session_id: params.sessionId,
        agent_id: params.agentId,
        risk_tier: params.riskTier ?? "medium",
        declared_intent: params.declaredIntent ?? "",
      },
      { onConflict: "session_id" }
    );
  if (error) throw error;
  console.error(`[arifOS] Session opened: ${params.sessionId} agent=${params.agentId}`);
}

export async function sealSession(params: {
  sessionId: string;
  finalVerdict: string;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb
    .from("arifosmcp_sessions")
    .update({
      final_verdict: params.finalVerdict,
      closed_at: new Date().toISOString(),
    })
    .eq("session_id", params.sessionId);
  if (error) throw error;
  console.error(`[arifOS] Session sealed: ${params.sessionId} verdict=${params.finalVerdict}`);
}

// ── TOOL CALLS ─────────────────────────────────────────────────────────────────

export async function logToolCall(record: {
  runId?: string;
  sessionId: string;
  toolName: string;
  organ?: string;
  toolArgs?: Record<string, unknown>;
  toolResult?: string;
  durationMs: number;
  floorTriggered: string[];
  verdict: string;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb.from("arifosmcp_tool_calls").insert({
    run_id: record.runId ?? null,
    session_id: record.sessionId,
    tool_name: record.toolName,
    organ: record.organ ?? null,
    tool_args: record.toolArgs ?? null,
    tool_result: record.toolResult ?? null,
    duration_ms: record.durationMs,
    floor_triggered: record.floorTriggered,
    verdict: record.verdict,
  });
  if (error) throw error;
}

// ── CANON RECORDS ───────────────────────────────────────────────────────────────

export async function writeCanonRecord(record: {
  adrId: string;
  title: string;
  decision: string;
  rationale: string;
  agentId: string;
  sessionId: string;
  payload: Record<string, unknown>;
  sealedBy?: string;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb
    .from("arifosmcp_canon_records")
    .upsert(
      {
        adr_id: record.adrId,
        title: record.title,
        decision: record.decision,
        rationale: record.rationale,
        agent_id: record.agentId,
        session_id: record.sessionId,
        sealed_by: record.sealedBy ?? "Muhammad Arif bin Fazil",
        payload: record.payload,
      },
      { onConflict: "adr_id" }
    );
  if (error) throw error;
  console.error(`[arifOS] Canon record written: ${record.adrId}`);
}

// ── APPROVAL TICKETS ──────────────────────────────────────────────────────────

export async function createApprovalTicket(ticket: {
  ticketId: string;
  sessionId: string;
  status: string;
  riskLevel: string;
  intentModel: string;
  domain?: string;
  data: Record<string, unknown>;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb
    .from("arifosmcp_approval_tickets")
    .upsert(
      {
        ticket_id: ticket.ticketId,
        session_id: ticket.sessionId,
        status: ticket.status,
        risk_level: ticket.riskLevel,
        intent_model: ticket.intentModel,
        domain: ticket.domain ?? null,
        data: ticket.data,
      },
      { onConflict: "ticket_id" }
    );
  if (error) throw error;
}

export async function getApprovalTicket(ticketId: string): Promise<Record<string, unknown> | null> {
  const sb = createSupabaseClient();
  const { data, error } = await sb
    .from("arifosmcp_approval_tickets")
    .select("*")
    .eq("ticket_id", ticketId)
    .maybeSingle();
  if (error) throw error;
  return data;
}

export async function queryApprovalTickets(options?: {
  status?: string;
  sessionId?: string;
  riskLevel?: string;
}): Promise<Record<string, unknown>[]> {
  const sb = createSupabaseClient();
  let q = sb
    .from("arifosmcp_approval_tickets")
    .select("*")
    .order("created_at", { ascending: false });

  if (options?.status) q = q.eq("status", options.status);
  if (options?.sessionId) q = q.eq("session_id", options.sessionId);
  if (options?.riskLevel) q = q.eq("risk_level", options.riskLevel);

  const { data, error } = await q;
  if (error) throw error;
  return data ?? [];
}

// ── FLOOR RULES ────────────────────────────────────────────────────────────────

export async function loadFloorRules(): Promise<Record<string, unknown>[]> {
  const sb = createSupabaseClient();
  const { data, error } = await sb
    .from("arifosmcp_floor_rules")
    .select("*")
    .order("floor_id");
  if (error) throw error;
  return data ?? [];
}

// ── WEALTH ──────────────────────────────────────────────────────────────────────

export async function logTransaction(record: {
  txType: string;
  asset?: string;
  amount?: number;
  currency?: string;
  metadata?: Record<string, unknown>;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb.from("arifosmcp_transactions").insert({
    tx_type: record.txType,
    asset: record.asset ?? null,
    amount: record.amount ?? null,
    currency: record.currency ?? "MYR",
    metadata: record.metadata ?? {},
  });
  if (error) throw error;
}

export async function logPortfolioSnapshot(record: {
  holdings: Record<string, unknown>;
  totalValue?: number;
  currency?: string;
}): Promise<void> {
  const sb = createSupabaseClient();
  const { error } = await sb.from("arifosmcp_portfolio_snapshots").insert({
    holdings: record.holdings,
    total_value: record.totalValue ?? null,
    currency: record.currency ?? "MYR",
  });
  if (error) throw error;
}