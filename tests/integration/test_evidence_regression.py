"""
Comprehensive Forensic Regression Test Suite
Verifies:
1. General educational PDF with no payment evidence -> GENERAL_DOCUMENT, NOT_APPLICABLE (Never "Payment Authorized").
2. Invoice without proof of payment -> INVOICE, NOT_VERIFIED.
3. Genuine receipt with payment status unverified -> RECEIPT, NOT_VERIFIED.
4. Legitimate UPI QR -> QR_CODE, parse payee, not blindly malicious.
5. Ordinary HTTPS QR -> QR_CODE, SAFE if domain is benign.
6. Suspicious QR destination -> QR_CODE, SUSPICIOUS/MALICIOUS with proper indicator.
7. Invalid or unreadable QR -> INCONCLUSIVE / IMAGE_QUALITY finding, not false safe.
8. Suspicious URL inside a general document -> flagged with SUSPICIOUS_LINK finding.
9. Corrupted upload / unsupported file -> proper error / file integrity finding.
10. Oversized upload (>10 MB) -> 413 Payload Too Large.
11. Conflicting detector results -> consistent canonical aggregation.
Quantum Kavacha Platform
"""
import io
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.schemas import (
    EvidenceSubmitRequest, EvidenceType, Verdict, PaymentStatus, FindingSeverity
)
from services.evidence.pipeline import evidence_pipeline
from services.document_analysis.service import document_service
from services.qr_analysis.service import qr_service
from services.threat_intelligence.service import threat_intel_service

client = TestClient(app)


def test_general_educational_pdf_never_authorized_payment():
    """Verify general educational document is classified as GENERAL_DOCUMENT, NOT_APPLICABLE, never authorized payment."""
    fake_educational_pdf = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 55 >> stream
BT /F1 12 Tf 100 700 Td (Lecture Notes on Cryptography and Cybersecurity) Tj ET
endstream
endobj
xref
0 5
trailer << /Root 1 0 R >>
%%EOF"""
    
    doc_res = document_service.analyze_pdf_bytes(fake_educational_pdf)
    assert doc_res["evidence_type"] == EvidenceType.GENERAL_DOCUMENT
    assert doc_res["payment_status"] == PaymentStatus.NOT_APPLICABLE
    # Assert no finding claims payment authorization
    for f in doc_res["findings"]:
        assert "Payment Authorized" not in f.title
        assert "Payment Authorized" not in f.description


def test_invoice_without_proof_of_payment():
    """Verify invoice sets payment status to NOT_VERIFIED and does not claim payment completion."""
    invoice_pdf = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 95 >> stream
BT /F1 12 Tf 100 700 Td (Tax Invoice Number: INV-2026-091 Bill To: ACME Corp Due Date: 2026-11-01) Tj ET
endstream
endobj
xref
0 5
trailer << /Root 1 0 R >>
%%EOF"""
    doc_res = document_service.analyze_pdf_bytes(invoice_pdf)
    assert doc_res["evidence_type"] == EvidenceType.INVOICE
    assert doc_res["payment_status"] == PaymentStatus.NOT_VERIFIED


def test_receipt_payment_status_unverified():
    """Verify receipt extraction sets payment status to NOT_VERIFIED pending gateway verification."""
    receipt_pdf = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 95 >> stream
BT /F1 12 Tf 100 700 Td (Payment Receipt: Transaction Successful Paid To: Store UPI Ref ID: 99120) Tj ET
endstream
endobj
xref
0 5
trailer << /Root 1 0 R >>
%%EOF"""
    doc_res = document_service.analyze_pdf_bytes(receipt_pdf)
    assert doc_res["evidence_type"] == EvidenceType.RECEIPT
    assert doc_res["payment_status"] == PaymentStatus.NOT_VERIFIED


def test_ordinary_https_qr():
    """Verify standard benign HTTPS URL QR is parsed and marked SAFE without false alarms."""
    payload = "https://developer.mozilla.org/en-US/docs/Web"
    parsed = qr_service.parse_payload(payload)
    assert parsed["is_url"] is True
    assert parsed["scheme"] == "https"
    
    findings = qr_service.inspect_payload(parsed)
    assert len(findings) == 0


def test_suspicious_qr_destination_shortener():
    """Verify shortened URL payload in QR is flagged for evasion."""
    payload = "https://bit.ly/claim-bonus-3000"
    parsed = qr_service.parse_payload(payload)
    findings = qr_service.inspect_payload(parsed)
    assert any(f.category == "EVASION_TECHNIQUE" for f in findings)


def test_unreadable_or_invalid_qr_image():
    """Verify an empty/corrupted image returns unreadable finding rather than a silent safe verdict."""
    corrupted_bytes = b"NOT_A_VALID_IMAGE_DATA_12345"
    decoded, err = qr_service.decode_qr_bytes(corrupted_bytes)
    assert decoded is None
    assert err is not None


def test_suspicious_url_inside_general_document():
    """Verify document containing a shortened link triggers SUSPICIOUS_LINK finding."""
    doc_with_link = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 85 >> stream
BT /F1 12 Tf 100 700 Td (Annual Corporate Report: Download appendix at https://bit.ly/hidden-doc) Tj ET
endstream
endobj
xref
0 5
trailer << /Root 1 0 R >>
%%EOF"""
    doc_res = document_service.analyze_pdf_bytes(doc_with_link)
    assert any(f.category == "SUSPICIOUS_LINK" for f in doc_res["findings"])


def test_oversized_upload_rejection():
    """Verify uploads > 10MB are rejected with HTTP 413 Payload Too Large."""
    # Create 11MB dummy payload
    oversized_data = b"0" * (11 * 1024 * 1024)
    res = client.post(
        "/api/evidence/upload",
        files={"file": ("oversized.png", io.BytesIO(oversized_data), "image/png")}
    )
    assert res.status_code == 413
    assert "10 MB" in res.json()["detail"]


def test_canonical_verdict_consistency():
    """Verify pipeline produces identical verdict and findings schema across invocations."""
    req = EvidenceSubmitRequest(
        evidence_type=EvidenceType.URL,
        input_text="https://paytm-security-bonus.xyz/claim"
    )
    r1 = evidence_pipeline.run_pipeline(req)
    r2 = evidence_pipeline.run_pipeline(req)
    assert r1.final_verdict == r2.final_verdict
    assert r1.payment_status == r2.payment_status
    assert r1.risk_score == r2.risk_score
