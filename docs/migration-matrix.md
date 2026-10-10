# MIGRATION MATRIX & AUDIT REPORT

## 1. Executive Summary & Old Codebase Audit
**Source Directory:** `S:\QK\QUANTUM-KAVACHA-main\QUANTUM-KAVACHA-main`  
**Target Repository:** `S:\QK\Final` (`quantum-kavacha-platform`)

The legacy codebase suffered from key architectural issues:
1. **False Positive & Verdict Inconsistencies:** Documents with benign or missing transactions were classified with fabricated verdicts (e.g. general educational PDFs misclassified as authorized payments or false alarms).
2. **Payment Settlement Confusion:** OCR extraction of text was presented as authoritative proof that a payment actually succeeded, lacking settlement boundary disclaimers.
3. **UI / UX Complexity:** A permanent dark-blue sidebar with overly technical terms, flashing animations, and no clear guided customer workflow.
4. **Hardcoded Metrics & Disconnected Micro-states:** Screens frequently fell back to mock data arrays rather than unified backend case persistence.
5. **Incomplete Localization:** Only partial translation files existed, leaving UI labels broken or untranslated.

---

## 2. Component Migration Decision Matrix

| Legacy Component / Service | Status | Reason & Action Taken |
| :--- | :--- | :--- |
| `backend/app/services/gemini_evidence_service.py` | **Refactor & Retain** | Magic bytes validation, EXIF tampering checks, and prompt-injection guardrails are sound. Needs typed integration with the canonical `EvidenceAnalysisResult` contract. |
| `backend/app/services/payment_forensics.py` | **Refactor & Retain** | QR decoding with OpenCV and UPI URI parsing are solid. Must decouple OCR from claimed payment verification. |
| `backend/app/services/threat_intel_service.py` | **Refactor & Retain** | URL domain reputation and entropy calculations work; add explicit handling for offline/outage states without silent safe verdicts. |
| `backend/app/services/quantum_benchmark.py` | **Isolate to Research Lab** | Qiskit circuit routines work in simulation mode. Must be kept out of the everyday customer flow and explicitly labeled as research. |
| `frontend/src/components/*` (12 legacy tabs) | **Redesign from Scratch** | Replaced with clean horizontal navigation (Overview, Analyze Evidence, Investigations, Threat Intelligence, Research Lab, Reports, Settings, plus Analyst Tools dropdown). |
| Hardcoded sample data in views | **Reject** | Replaced with live backend persistence (SQLite / in-memory case database) and structured empty states. |
| Legacy left navigation sidebar | **Reject** | Replaced with mandatory top header + horizontal sub-navigation. |

---

## 3. Strict Verdict Rules

1. **General / Educational PDF:**
   - Classification: `GENERAL_DOCUMENT`
   - Payment Status: `NOT_APPLICABLE`
   - Threat Verdict: `SAFE` or `SUSPICIOUS` (based only on document anomalies, links, or macros). Never report as `Payment Authorized`.
2. **Invoices & Unverified Receipts:**
   - Payment Status: `NOT_VERIFIED`
   - Threat Verdict: Evaluated on tampering, suspicious links, or amount discrepancies. OCR extraction does not constitute proof of settlement.
3. **QR Codes:**
   - Preserves raw payload. Parsed UPI schemes and HTTPS URLs are checked for deceptive domains and redirects.
   - Genuine UPI or benign HTTPS URLs without malicious indicators are assessed as `SAFE` (not automatically flagged).
4. **Provider Failures:**
   - Timeouts or missing services yield `AnalysisStatus: PARTIAL` or `INCONCLUSIVE` with explicit limitations listed, never silent safe defaults.
