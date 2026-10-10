/**
 * Canonical Evidence Analysis and Investigation Contracts
 * Quantum Kavacha Platform
 */

export type EvidenceType =
  | "QR_CODE"
  | "URL"
  | "PAYMENT_SCREENSHOT"
  | "RECEIPT"
  | "INVOICE"
  | "TRANSACTION_RECORD"
  | "BANK_STATEMENT"
  | "GENERAL_DOCUMENT"
  | "IMAGE"
  | "UNKNOWN";

export type Verdict =
  | "SAFE"
  | "SUSPICIOUS"
  | "MALICIOUS"
  | "INCONCLUSIVE";

export type AnalysisStatus =
  | "COMPLETED"
  | "PARTIAL"
  | "FAILED";

export type PaymentStatus =
  | "VERIFIED"
  | "NOT_VERIFIED"
  | "NOT_APPLICABLE"
  | "UNKNOWN";

export type FindingSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface EvidenceFinding {
  id: string;
  category: string;
  severity: FindingSeverity;
  title: string;
  description: string;
  detector: string;
  evidence_excerpt?: string;
  confidence?: number;
}

export interface ModelStatus {
  detector_name: string;
  status: "EXECUTED" | "SKIPPED" | "UNAVAILABLE" | "FAILED";
  latency_ms: number;
  details?: string;
}

export interface ExtractedEntities {
  merchant?: string;
  amount?: number;
  currency?: string;
  transaction_id?: string;
  timestamp?: string;
  recipient_vpa?: string;
  sender_vpa?: string;
  raw_qr_payload?: string;
  destination_url?: string;
  document_type?: string;
}

export interface EvidenceAnalysisResult {
  case_id: string;
  created_at: string;
  evidence_type: EvidenceType;
  transaction_detected: boolean | null;
  final_verdict: Verdict;
  risk_score: number | null; // 0.0 - 100.0 scale
  confidence: number | null; // 0.0 - 1.0 scale
  reason_codes: string[];
  summary: string;
  evidence_findings: EvidenceFinding[];
  extracted_entities: ExtractedEntities;
  model_status: Record<string, ModelStatus>;
  analysis_status: AnalysisStatus;
  payment_status: PaymentStatus;
  limitations: string[];
  recommended_actions: string[];
}
