// All requests go through the Next.js rewrite proxy at /api -> backend.
const BASE = "/api";

export type GateStatus = "allowed" | "warned" | "needs_review" | "rejected";

export interface Citation {
  doc_id: string;
  snippet: string;
  score: number;
}

export interface Evaluation {
  faithfulness: number;
  citation_coverage: number;
  policy_score: number;
  passed: boolean;
  failed_checks: string[];
  policy: string;
  judge: string;
  rationale: string | null;
}

export interface DomainPolicy {
  domain: string;
  description: string;
  min_faithfulness: number;
  min_citation_coverage: number;
  min_policy_score: number;
  require_citations: boolean;
  banned_claims: string[];
}

export interface CompletionResponse {
  decision_id: string;
  status: GateStatus;
  output: string;
  provider: string;
  risk_level: string;
  citations: Citation[];
  evaluation: Evaluation;
  cost_usd: number;
  latency_ms: number;
  cached: boolean;
  created_at: string;
}

export interface LedgerEntry {
  decision_id: string;
  status: GateStatus;
  gate_status: GateStatus;
  risk_level: string;
  provider: string;
  domain: string | null;
  input_hash: string;
  evidence_hash: string;
  output_hash: string;
  decision_hash: string;
  prev_hash: string | null;
  faithfulness: number;
  citation_coverage: number;
  policy_score: number;
  cost_usd: number;
  latency_ms: number;
  cached: boolean;
  reviewer: string | null;
  review_decision: string | null;
  review_note: string | null;
  created_at: string;
  reviewed_at: string | null;
}

async function j<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  meta: () => fetch(`${BASE}/`).then(j<any>),
  complete: (body: {
    prompt: string;
    risk_level: string;
    domain?: string;
    use_rag: boolean;
    provider?: string;
  }) =>
    fetch(`${BASE}/ai/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(j<CompletionResponse>),
  policies: () => fetch(`${BASE}/policies`).then(j<DomainPolicy[]>),
  ledger: () => fetch(`${BASE}/ledger?limit=100`).then(j<LedgerEntry[]>),
  verify: () => fetch(`${BASE}/ledger/verify`).then(j<any>),
  reviewQueue: () => fetch(`${BASE}/review/queue`).then(j<LedgerEntry[]>),
  review: (
    id: string,
    body: { decision: string; reviewer: string; note?: string },
  ) =>
    fetch(`${BASE}/review/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(j<LedgerEntry>),
};
