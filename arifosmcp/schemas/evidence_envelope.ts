/**
 * arifOS EvidenceEnvelope — Universal Evidence Contract v1 (TypeScript)
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * The single mandatory envelope carried by every memory write, retrieval
 * result, Graphiti edge, external MCP response, and VAULT999 seal candidate.
 *
 * This is the TypeScript twin of evidence_envelope.py — same schema,
 * same enums, same invariants. Used by A-FORGE, Qwen Code, and any
 * TypeScript-native agent in the federation.
 *
 * Hard law (F13):
 *   - "Memory is not truth until provenance. Truth is not final until L6."
 *   - One writer implementation, at least one independent verifier.
 *   - No model lane may independently promote M3 or M4.
 *   - L3 retrieval similarity is never evidence.
 *
 * DITEMPA BUKAN DIBERI — Forged, Not Given
 */

import { createHash, randomUUID } from "node:crypto";

// ═══════════════════════════════════════════════════════════════════════════════
// ENUMS
// ═══════════════════════════════════════════════════════════════════════════════

export type MemoryTier = "M0" | "M1" | "M2" | "M3" | "M4";

export type StorageLayer = "L1" | "L2" | "L3" | "L4" | "L5" | "L6";

export type SourceType = "human" | "tool" | "document" | "model" | "sensor" | "derived";

export type DerivationMethod = "direct" | "extracted" | "inferred" | "aggregated";

export type AuthorityClass = "unverified" | "corroborated" | "authoritative" | "sealed";

export type PolicyLabel =
  | "internal"
  | "sensitive"
  | "external-shareable"
  | "constitutional"
  | "biometric"
  | "financial"
  | "geophysical";

// ═══════════════════════════════════════════════════════════════════════════════
// SUB-TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface Derivation {
  method: DerivationMethod;
  parent_event_ids: string[];
  model_id: string | null;
  tool_id: string | null;
}

export interface Integrity {
  canonical_hash: string;
  previous_seal: string | null;
  signature: string | null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CORE EVIDENCE ENVELOPE
// ═══════════════════════════════════════════════════════════════════════════════

export interface EvidenceEnvelope {
  /** Unique event identifier (uuid) */
  event_id: string;

  /** Correlation ID across the full evidence chain */
  trace_id: string;

  /** Agent or human identity that produced this evidence */
  actor_id: string;

  /** Federation tenant (default: arifos) */
  tenant_id: string;

  /** Memory risk tier (M0-M4) */
  memory_tier: MemoryTier;

  /** Target storage layer (L1-L6) */
  storage_layer: StorageLayer;

  /** Atomic, testable assertion — the actual evidence content */
  claim: string;

  /** Who or what asserted this evidence */
  source_type: SourceType;

  /** Immutable reference or source URI */
  source_locator: string;

  /** SHA-256 of the source material */
  source_hash: string;

  /** When the evidence was observed (ISO-8601) */
  observed_at: string;

  /** When this envelope was created (ISO-8601) */
  recorded_at: string;

  /** When this claim becomes valid (null = now) */
  valid_from: string | null;

  /** When this claim expires (null = never) */
  valid_until: string | null;

  /** Lineage and derivation metadata */
  derivation: Derivation;

  /** Confidence in this evidence (0.0-1.0) */
  confidence: number;

  /** Trust classification */
  authority_class: AuthorityClass;

  /** Access control and lifecycle labels */
  policy_labels: PolicyLabel[];

  /** Cryptographic integrity */
  integrity: Integrity;

  /** Constitutional floors activated by this evidence */
  floors: string[];

  /** Does this require 888-APEX judgment before promotion? */
  requires_888: boolean;

  /** VAULT999 event ID if sealed */
  vault_event_id: string | null;

  /** Organ-specific extensions */
  extensions: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════════
// FACTORY + HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

export function computeCanonicalHash(claim: string): string {
  return "sha256:" + createHash("sha256").update(claim, "utf-8").digest("hex");
}

export function createEvidenceEnvelope(
  overrides: Partial<EvidenceEnvelope> & Pick<EvidenceEnvelope, "actor_id" | "claim" | "source_type" | "source_locator">,
): EvidenceEnvelope {
  const now = new Date().toISOString();
  const claim = overrides.claim;
  const envelope: EvidenceEnvelope = {
    event_id: randomUUID(),
    trace_id: randomUUID(),
    actor_id: overrides.actor_id,
    tenant_id: overrides.tenant_id ?? "arifos",
    memory_tier: overrides.memory_tier ?? "M1",
    storage_layer: overrides.storage_layer ?? "L3",
    claim,
    source_type: overrides.source_type,
    source_locator: overrides.source_locator,
    source_hash: overrides.source_hash ?? "",
    observed_at: overrides.observed_at ?? now,
    recorded_at: overrides.recorded_at ?? now,
    valid_from: overrides.valid_from ?? null,
    valid_until: overrides.valid_until ?? null,
    derivation: overrides.derivation ?? {
      method: "direct",
      parent_event_ids: [],
      model_id: null,
      tool_id: null,
    },
    confidence: overrides.confidence ?? 0.5,
    authority_class: overrides.authority_class ?? "unverified",
    policy_labels: overrides.policy_labels ?? ["internal"],
    integrity: overrides.integrity ?? {
      canonical_hash: computeCanonicalHash(claim),
      previous_seal: null,
      signature: null,
    },
    floors: overrides.floors ?? [],
    requires_888: overrides.requires_888 ?? false,
    vault_event_id: overrides.vault_event_id ?? null,
    extensions: overrides.extensions ?? {},
  };

  // Ensure canonical hash is computed
  if (!envelope.integrity.canonical_hash) {
    envelope.integrity.canonical_hash = computeCanonicalHash(claim);
  }

  return envelope;
}

// ═══════════════════════════════════════════════════════════════════════════════
// TEMPORAL HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

export function isExpired(envelope: EvidenceEnvelope, at?: string): boolean {
  if (!envelope.valid_until) return false;
  const ref = at ? new Date(at) : new Date();
  return ref > new Date(envelope.valid_until);
}

export function isValid(envelope: EvidenceEnvelope, at?: string): boolean {
  const ref = at ? new Date(at) : new Date();
  if (envelope.valid_until && ref > new Date(envelope.valid_until)) return false;
  if (envelope.valid_from && ref < new Date(envelope.valid_from)) return false;
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONVERSION HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

export function toQdrantPayload(envelope: EvidenceEnvelope): Record<string, unknown> {
  return {
    event_id: envelope.event_id,
    trace_id: envelope.trace_id,
    actor_id: envelope.actor_id,
    tenant_id: envelope.tenant_id,
    memory_tier: envelope.memory_tier,
    storage_layer: envelope.storage_layer,
    claim: envelope.claim,
    source_type: envelope.source_type,
    source_locator: envelope.source_locator,
    source_hash: envelope.source_hash,
    observed_at: envelope.observed_at,
    recorded_at: envelope.recorded_at,
    valid_from: envelope.valid_from,
    valid_until: envelope.valid_until,
    derivation_method: envelope.derivation.method,
    parent_event_ids: envelope.derivation.parent_event_ids,
    model_id: envelope.derivation.model_id,
    tool_id: envelope.derivation.tool_id,
    confidence: envelope.confidence,
    authority_class: envelope.authority_class,
    policy_labels: envelope.policy_labels,
    canonical_hash: envelope.integrity.canonical_hash,
    previous_seal: envelope.integrity.previous_seal,
    signature: envelope.integrity.signature,
    floors: envelope.floors,
    requires_888: envelope.requires_888,
    vault_event_id: envelope.vault_event_id,
  };
}

export function toGraphitiEdge(envelope: EvidenceEnvelope): Record<string, unknown> {
  return {
    event_id: envelope.event_id,
    trace_id: envelope.trace_id,
    actor_id: envelope.actor_id,
    claim: envelope.claim,
    confidence: envelope.confidence,
    authority_class: envelope.authority_class,
    valid_from: envelope.valid_from,
    valid_until: envelope.valid_until,
    source_event_ids: envelope.derivation.parent_event_ids,
    observed_at: envelope.observed_at,
    is_expired: isExpired(envelope),
    canonical_hash: envelope.integrity.canonical_hash,
  };
}

export function toVaultCandidate(envelope: EvidenceEnvelope): Record<string, unknown> {
  return {
    event_id: envelope.event_id,
    trace_id: envelope.trace_id,
    actor_id: envelope.actor_id,
    tenant_id: envelope.tenant_id,
    memory_tier: envelope.memory_tier,
    storage_layer: "L6" as StorageLayer,
    claim: envelope.claim,
    source_type: envelope.source_type,
    source_locator: envelope.source_locator,
    source_hash: envelope.source_hash,
    observed_at: envelope.observed_at,
    recorded_at: envelope.recorded_at,
    valid_from: envelope.valid_from,
    valid_until: envelope.valid_until,
    derivation: {
      method: envelope.derivation.method,
      parent_event_ids: envelope.derivation.parent_event_ids,
      model_id: envelope.derivation.model_id,
      tool_id: envelope.derivation.tool_id,
    },
    confidence: envelope.confidence,
    authority_class: envelope.authority_class,
    policy_labels: envelope.policy_labels,
    floors: envelope.floors,
    requires_888: envelope.requires_888,
    integrity: {
      canonical_hash: envelope.integrity.canonical_hash,
      previous_seal: envelope.integrity.previous_seal,
      signature: envelope.integrity.signature,
    },
    extensions: envelope.extensions,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// TIER-LAYER ALLOWANCE
// ═══════════════════════════════════════════════════════════════════════════════

const TIER_LAYER_ALLOWANCE: Record<MemoryTier, StorageLayer[]> = {
  M0: ["L1", "L2"],
  M1: ["L1", "L2", "L3"],
  M2: ["L3", "L4"],
  M3: ["L4", "L5"],
  M4: ["L6"],
};

export function tierLayerAllowed(tier: MemoryTier, layer: StorageLayer): boolean {
  return TIER_LAYER_ALLOWANCE[tier]?.includes(layer) ?? false;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PROVENANCE-AWARE RETRIEVAL SCORING
// ═══════════════════════════════════════════════════════════════════════════════

const AUTHORITY_WEIGHTS: Record<AuthorityClass, number> = {
  unverified: 0.5,
  corroborated: 0.8,
  authoritative: 1.0,
  sealed: 1.0,
};

export function provenanceScore(
  envelope: EvidenceEnvelope,
  semanticRelevance: number = 0,
  freshnessDays: number | null = null,
  corroborationCount: number = 0,
): number {
  const authorityWeight = AUTHORITY_WEIGHTS[envelope.authority_class] ?? 0.5;

  const freshness =
    freshnessDays === null
      ? 1.0
      : Math.max(0.1, Math.exp(-freshnessDays / 90));

  const corroborationBonus = 1.0 + 0.1 * Math.min(corroborationCount, 10);

  const validityPenalty = isValid(envelope) ? 1.0 : 0.0;

  const score =
    semanticRelevance *
    authorityWeight *
    freshness *
    corroborationBonus *
    validityPenalty;

  return Math.round(Math.min(score, 2.0) * 10000) / 10000;
}
