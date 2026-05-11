/**
 * arifOS Canonical Stack Interface v2.1
 * "Governed Intelligence Above Generative Intelligence"
 */

export enum MetabolicStage {
  INGEST_000 = '000_INGEST',
  CLEAN_111 = '111_CLEAN',
  NORMALIZE_222 = '222_NORMALIZE',
  FEAT_ENG_333 = '333_FEAT_ENG',
  EMBED_444 = '444_EMBED',
  RAG_555 = '555_RAG',
  INVOKE_666 = '666_INVOKE',
  JUDGE_777 = '777_JUDGE',
  HOLD_888 = '888_HOLD',
  LEDGER_999 = '999_LEDGER',
}

export interface IArifosKernel {
  floors: {
    delta: number; // Clarity
    omega: number; // Humility
    psi: number;   // Vitality
  };
  gates: {
    reversibility: number;
    truth_confidence: number;
    sovereign_override: boolean;
  };
}

export interface IArifosStack {
  ui: {
    language: 'TypeScript';
    packageManager: 'npm';
    safety: 'WebMCP';
  };
  kernel: {
    logic: 'arifOS Kernel';
    config: 'YAML';
    transport: 'Protobuf/gRPC';
    interchange: 'JSON';
  };
  pipeline: {
    runtime: 'Python';
    stages: MetabolicStage[];
  };
  foundations: {
    storage: 'SQL';
    analytics: 'Parquet/Arrow';
    grounding: 'ACID';
  };
  engine: {
    architecture: 'Transformer';
    semantics: 'Embeddings';
    method: 'Self-Attention';
  };
}
