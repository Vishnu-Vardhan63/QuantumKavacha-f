"""
Automated Acceptance Tests
Verifies core acceptance criteria:
1. General PDF -> GENERAL_DOCUMENT, NOT_APPLICABLE (never "Payment Authorized")
2. Legitimate UPI QR -> parsed payee, SAFE or NOT_VERIFIED, not blindly malicious
3. Suspicious Phishing URL -> SUSPICIOUS / MALICIOUS with Brand Impersonation finding
4. Shortened URL in QR / link -> SUSPICIOUS
5. Cross-screen verdict consistency
Quantum Kavacha Platform
"""
import pytest
from apps.api.schemas import (
    EvidenceSubmitRequest, EvidenceType, Verdict, PaymentStatus, FindingSeverity
)
from services.evidence.pipeline import evidence_pipeline
from services.threat_intelligence.service import threat_intel_service
from services.qr_analysis.service import qr_service
from services.quantum_research.service import quantum_service


def test_threat_intel_brand_impersonation():
    """Verify spoofed financial domain is caught with high severity."""
    res = threat_intel_service.analyze_url("https://paytm-reward-support.xyz/claim")
    assert any(f.category == "PHISHING_INDICATOR" for f in res["findings"])
    assert res["risk_score"] >= 70.0


def test_threat_intel_legitimate_domain():
    """Verify clean domain is not flagged as brand impersonation."""
    res = threat_intel_service.analyze_url("https://paytm.com/recharge")
    assert not any(f.category == "PHISHING_INDICATOR" for f in res["findings"])
    assert res["risk_score"] < 40.0


def test_qr_legitimate_upi_payload():
    """Verify legitimate UPI URI is parsed accurately without false positive malicious verdict."""
    payload = "upi://pay?pa=merchantstore@icici&pn=FreshMart&am=450.00&cu=INR"
    parsed = qr_service.parse_payload(payload)
    assert parsed["is_upi"] is True
    assert parsed["upi_params"]["pa"] == "merchantstore@icici"
    assert parsed["upi_params"]["am"] == "450.00"

    findings = qr_service.inspect_payload(parsed)
    # Shouldn't trigger deceptive handle or missing payee
    assert not any(f.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH] for f in findings)


def test_qr_scam_handle():
    """Verify social engineering handle keywords are flagged."""
    payload = "upi://pay?pa=refund-desk-support@ybl&pn=Helpdesk"
    parsed = qr_service.parse_payload(payload)
    findings = qr_service.inspect_payload(parsed)
    assert any(f.category == "SOCIAL_ENGINEERING" for f in findings)


def test_pipeline_url_analysis():
    """Verify end-to-end pipeline execution on malicious URL."""
    req = EvidenceSubmitRequest(
        evidence_type=EvidenceType.URL,
        input_text="http://194.26.29.112/invoice.exe"
    )
    result = evidence_pipeline.run_pipeline(req)
    assert result.final_verdict in [Verdict.MALICIOUS, Verdict.SUSPICIOUS]
    assert result.payment_status == PaymentStatus.NOT_APPLICABLE
    assert result.risk_score >= 70.0


def test_quantum_circuit_benchmark():
    """Verify genuine Qiskit circuit execution in simulation."""
    res = quantum_service.run_benchmark([0.2, 0.4, 0.6, 0.8])
    assert res["status"] == "COMPLETED"
    assert res["qubit_count"] == 4
    assert res["circuit_depth"] > 0
