/**
 * AgentMessage — A2A communication envelope
 * DITEMPA BUKAN DIBERI
 */

import { EpistemicTag } from "./epistemic.js";

export type MessageType =
  | "task"
  | "result"
  | "query"
  | "ack"
  | "hold"
  | "abort"
  | "status";

export interface AgentMessage {
  message_id: string;
  sender_id: string;
  receiver_id: string;
  session_id: string;
  task_id: string;
  subtask_id: string | null;
  parent_message_id: string | null;
  message_type: MessageType;
  payload: Record<string, unknown>;
  schema_ref: string | null;
  maruah_score: number;
  epistemic: EpistemicTag;
  floor_violations: string[];
  irreversible: boolean;
  timestamp: string;
  ttl_seconds: number;
  expires_at: string;
  ack_required: boolean;
  ack_received: boolean;
  ack_timestamp: string | null;
}

export interface SendAgentMessageInput {
  sender_id: string;
  receiver_id: string;
  task_id: string;
  session_id: string;
  message_type: MessageType;
  payload: Record<string, unknown>;
  maruah_score: number;
  epistemic?: EpistemicTag;
  irreversible?: boolean;
  ttl_seconds?: number;
}

export interface SendAgentMessageOutput {
  message_id: string;
  status: "sent" | "rejected" | "held";
  rejection_reason: string | null;
  hold_triggered: boolean;
  expires_at: string;
  vault_record_id: string;
}

export function validateAgentMessage(msg: Partial<AgentMessage>): string[] {
  const errors: string[] = [];

  if (msg.maruah_score !== undefined && msg.maruah_score < 0.5) {
    errors.push("MARUAH_FAIL: maruah_score must be >= 0.5");
  }

  if (msg.ttl_seconds !== undefined && msg.ttl_seconds > 3600) {
    errors.push("TTL_EXCEEDED: ttl_seconds max is 3600");
  }

  if (msg.irreversible && !msg.ack_required) {
    errors.push("IRREVERSIBLE_REQUIRES_ACK: irreversible messages must set ack_required=true");
  }

  return errors;
}