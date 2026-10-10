"""
Authoritative Evidence Analysis Pipeline & Verdict Aggregation
Orchestrates Input -> Validation -> Classification -> Specialized Analysis ->
Finding Normalization -> Canonical Aggregation -> Persistence.
Quantum Kavacha Platform
"""
import uuid
import base64
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from apps.api.schemas import (
    EvidenceAnalysisResult, EvidenceType, Verdict, AnalysisStatus,
    PaymentStatus, EvidenceFinding, FindingSeverity, ModelStatus,
    ExtractedEntities, EvidenceSubmitRequest
)
from services.qr_analysis.service import qr_service
from services.threat_intelligence.service import threat_intel_service
from services.document_analysis.service import document_service
from services.payment_forensics.service import image_forensics_service


class EvidencePipeline:
    def __init__(self):
        pass

    def run_pipeline(self, request: EvidenceSubmitRequest) -> EvidenceAnalysisResult:
        case_id = f"QK-CASE-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()
        
        findings: List[EvidenceFinding] = []
        model_status: Dict[str, ModelStatus] = {}
        limitations: List[str] = [
            "Settlement Limitation: Analysis of screenshots, QR codes, or documents cannot verify fund settlement without an authoritative bank gateway."
        ]
        recommended_actions: List[str] = []
        reason_codes: List[str] = []
        extracted_entities = ExtractedEntities()
        
        input_text = request.input_text.strip() if request.input_text else None
        image_bytes = None
        if request.image_base64:
            try:
                # Handle data URI if present
                b64 = request.image_base64
                if "," in b64:
                    b64 = b64.split(",", 1)[1]
                image_bytes = base64.b64decode(b64)
            except Exception:
                image_bytes = None

        filename = request.filename.lower() if request.filename else ""
        
        # 1. Evidence Type Determination
        determined_type = request.evidence_type or EvidenceType.UNKNOWN
        
        if determined_type == EvidenceType.UNKNOWN:
            if filename.endswith(".pdf") or (image_bytes and image_bytes.startswith(b"%PDF")):
                determined_type = EvidenceType.GENERAL_DOCUMENT
            elif input_text and (input_text.startswith("http://") or input_text.startswith("https://") or " " not in input_text and "." in input_text):
                determined_type = EvidenceType.URL
            elif input_text and input_text.startswith("upi://"):
                determined_type = EvidenceType.QR_CODE
            elif image_bytes:
                # Check if it contains a QR code first
                decoded_qr, _ = qr_service.decode_qr_bytes(image_bytes)
                if decoded_qr:
                    determined_type = EvidenceType.QR_CODE
                else:
                    determined_type = EvidenceType.IMAGE

        # 2. Specialized Analysis Execution
        payment_status = PaymentStatus.UNKNOWN
        transaction_detected = False

        # --- PATH A: URL ANALYSIS ---
        if determined_type == EvidenceType.URL or (input_text and (input_text.startswith("http://") or input_text.startswith("https://"))):
            determined_type = EvidenceType.URL
            t0 = time.time()
            url_res = threat_intel_service.analyze_url(input_text or "")
            t_ms = (time.time() - t0) * 1000.0
            
            findings.extend(url_res["findings"])
            extracted_entities.destination_url = url_res.get("url")
            model_status["ThreatIntelligenceService"] = ModelStatus(
                detector_name="ThreatIntelligenceService",
                status="EXECUTED",
                latency_ms=round(t_ms, 2)
            )
            payment_status = PaymentStatus.NOT_APPLICABLE
            limitations.append("Threat intelligence reputation is checked against heuristic indicators and known risk patterns.")

        # --- PATH B: QR CODE ANALYSIS ---
        elif determined_type == EvidenceType.QR_CODE or (image_bytes and qr_service.decode_qr_bytes(image_bytes)[0]):
            determined_type = EvidenceType.QR_CODE
            t0 = time.time()
            raw_payload = None
            
            if image_bytes:
                decoded_text, err = qr_service.decode_qr_bytes(image_bytes)
                if decoded_text:
                    raw_payload = decoded_text
                else:
                    findings.append(EvidenceFinding(
                        id="FIND-QR-UNREADABLE",
                        category="IMAGE_QUALITY",
                        severity=FindingSeverity.MEDIUM,
                        title="Unreadable or Missing QR Code",
                        description=err or "Could not decode any standard QR pattern from the image.",
                        detector="QRAnalysisService"
                    ))
            elif input_text:
                raw_payload = input_text

            if raw_payload:
                extracted_entities.raw_qr_payload = raw_payload
                parsed = qr_service.parse_payload(raw_payload)
                qr_findings = qr_service.inspect_payload(parsed)
                findings.extend(qr_findings)
                
                if parsed.get("is_upi"):
                    transaction_detected = True
                    payment_status = PaymentStatus.NOT_VERIFIED
                    upi = parsed.get("upi_params", {})
                    extracted_entities.recipient_vpa = upi.get("pa")
                    extracted_entities.merchant = upi.get("pn")
                    if upi.get("am"):
                        try:
                            extracted_entities.amount = float(upi.get("am"))
                        except ValueError:
                            pass
                    extracted_entities.currency = upi.get("cu", "INR")
                elif parsed.get("is_url"):
                    extracted_entities.destination_url = raw_payload
                    url_res = threat_intel_service.analyze_url(raw_payload)
                    findings.extend(url_res["findings"])
                    payment_status = PaymentStatus.NOT_APPLICABLE
                else:
                    payment_status = PaymentStatus.NOT_APPLICABLE

            t_ms = (time.time() - t0) * 1000.0
            model_status["QRAnalysisService"] = ModelStatus(
                detector_name="QRAnalysisService",
                status="EXECUTED",
                latency_ms=round(t_ms, 2)
            )

        # --- PATH C: PDF / GENERAL DOCUMENT ---
        elif determined_type in [EvidenceType.GENERAL_DOCUMENT, EvidenceType.INVOICE, EvidenceType.BANK_STATEMENT] or filename.endswith(".pdf"):
            t0 = time.time()
            if image_bytes:
                doc_res = document_service.analyze_pdf_bytes(image_bytes)
                findings.extend(doc_res["findings"])
                determined_type = doc_res["evidence_type"]
                payment_status = doc_res["payment_status"]
                
                # If embedded URLs were found, analyze them
                for u in doc_res.get("extracted_urls", []):
                    u_eval = threat_intel_service.analyze_url(u)
                    findings.extend(u_eval["findings"])
                
                model_status["DocumentAnalysisService"] = ModelStatus(
                    detector_name="DocumentAnalysisService",
                    status="EXECUTED",
                    latency_ms=round((time.time() - t0) * 1000.0, 2)
                )
            else:
                findings.append(EvidenceFinding(
                    id="FIND-DOC-NO-DATA",
                    category="FILE_ERROR",
                    severity=FindingSeverity.HIGH,
                    title="No Document Content Received",
                    description="Empty payload for document inspection.",
                    detector="DocumentAnalysisService"
                ))

        # --- PATH D: IMAGE / SCREENSHOT FORENSICS ---
        elif image_bytes:
            t0 = time.time()
            img_res = image_forensics_service.inspect_image_bytes(image_bytes, filename=filename)
            findings.extend(img_res.get("findings", []))
            
            if img_res.get("is_screenshot_proportions"):
                determined_type = EvidenceType.PAYMENT_SCREENSHOT
                payment_status = PaymentStatus.NOT_VERIFIED
            else:
                determined_type = EvidenceType.IMAGE
                payment_status = PaymentStatus.NOT_APPLICABLE
                
            model_status["ImagePaymentForensicsService"] = ModelStatus(
                detector_name="ImagePaymentForensicsService",
                status="EXECUTED",
                latency_ms=round((time.time() - t0) * 1000.0, 2)
            )

        # 3. Canonical Verdict Aggregation
        # Critical findings -> MALICIOUS
        # High findings -> SUSPICIOUS
        # Medium findings -> SUSPICIOUS or INCONCLUSIVE depending on evidence
        # No adverse findings -> SAFE
        critical_count = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)
        medium_count = sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM)
        
        if critical_count > 0:
            final_verdict = Verdict.MALICIOUS
            risk_score = 92.0 + min(8.0, critical_count * 2.0)
            confidence = 0.95
            summary = "Confirmed high-severity malicious indicators detected."
            reason_codes.append("CRITICAL_THREAT_IDENTIFIED")
            recommended_actions.append("Do not open, interact with, or send funds to this destination.")
            recommended_actions.append("Block and report the indicator in internal threat monitoring.")
        elif high_count > 0:
            final_verdict = Verdict.SUSPICIOUS
            risk_score = 68.0 + min(20.0, high_count * 5.0)
            confidence = 0.85
            summary = "Suspicious or deceptive indicators detected. Manual review recommended before interacting."
            reason_codes.append("HIGH_RISK_ANOMALIES")
            recommended_actions.append("Exercise extreme caution. Verify the destination via an independent, out-of-band channel.")
        elif medium_count > 0:
            final_verdict = Verdict.SUSPICIOUS
            risk_score = 42.0 + min(20.0, medium_count * 5.0)
            confidence = 0.75
            summary = "Potential risk indicators observed requiring user discretion."
            reason_codes.append("MODERATE_RISK_FACTORS")
            recommended_actions.append("Confirm sender identity before taking action.")
        else:
            final_verdict = Verdict.SAFE
            risk_score = 5.0
            confidence = 0.90
            summary = "No significant threat indicators found in the automated checks performed."
            reason_codes.append("CLEAN_AUTOMATED_CHECKS")
            recommended_actions.append("Standard security hygiene applies.")

        # Special Case: Empty or unreadable findings
        if not findings and not input_text and not image_bytes:
            final_verdict = Verdict.INCONCLUSIVE
            risk_score = 0.0
            confidence = 0.0
            summary = "Evidence was insufficient or unsupported for definitive analysis."
            reason_codes.append("INSUFFICIENT_EVIDENCE")

        return EvidenceAnalysisResult(
            case_id=case_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            evidence_type=determined_type,
            transaction_detected=transaction_detected,
            final_verdict=final_verdict,
            risk_score=round(risk_score, 1),
            confidence=round(confidence, 2),
            reason_codes=reason_codes,
            summary=summary,
            evidence_findings=findings,
            extracted_entities=extracted_entities,
            model_status=model_status,
            analysis_status=AnalysisStatus.COMPLETED,
            payment_status=payment_status,
            limitations=limitations,
            recommended_actions=recommended_actions
        )


evidence_pipeline = EvidencePipeline()
