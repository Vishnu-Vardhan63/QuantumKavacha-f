"""
Document Analysis Service
Extracts text and inspects document structure, embedded links, and payment applicability.
Specifically guarantees that general documents (educational, business proposals, reports)
do NOT falsely assert 'Payment Authorized'.
Quantum Kavacha Platform
"""
import io
import re
from typing import Dict, Any, List, Optional
import pdfplumber
from apps.api.schemas import EvidenceFinding, FindingSeverity, EvidenceType, PaymentStatus


class DocumentAnalysisService:
    def __init__(self):
        # Keywords indicating an invoice
        self.invoice_keywords = ["invoice", "tax invoice", "bill to", "invoice number", "gstin", "subtotal", "due date"]
        # Keywords indicating a receipt/payment voucher
        self.receipt_keywords = ["payment receipt", "transaction successful", "paid to", "utr number", "upi ref id", "debited from"]
        # Keywords indicating a bank statement
        self.statement_keywords = ["account statement", "statement of account", "opening balance", "closing balance", "withdrawal", "deposit"]

    def analyze_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Parses PDF bytes, extracts text, finds embedded URLs, determines document category,
        and ensures payment status is explicitly handled.
        """
        findings: List[EvidenceFinding] = []
        extracted_text = ""
        page_count = 0
        extracted_urls = set()

        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                for page_idx, page in enumerate(pdf.pages):
                    t = page.extract_text() or ""
                    extracted_text += t + "\n"
                    
                    # Extract hyperlinks if available in page annotations
                    if hasattr(page, "hyperlinks") and page.hyperlinks:
                        for hl in page.hyperlinks:
                            uri = hl.get("uri")
                            if uri:
                                extracted_urls.add(uri)

            # Also scan raw text for regex URLs
            url_pattern = re.compile(r"https?://[^\s<>\"'()]+")
            for m in url_pattern.finditer(extracted_text):
                extracted_urls.add(m.group(0))

        except Exception as e:
            findings.append(EvidenceFinding(
                id="FIND-DOC-PARSE-ERR",
                category="DOCUMENT_INTEGRITY",
                severity=FindingSeverity.HIGH,
                title="Document Parsing Exception",
                description=f"Error reading PDF structure: {str(e)}",
                detector="DocumentAnalysisService"
            ))
            return {
                "success": False,
                "evidence_type": EvidenceType.GENERAL_DOCUMENT,
                "payment_status": PaymentStatus.NOT_APPLICABLE,
                "findings": findings,
                "extracted_text": "",
                "extracted_urls": []
            }

        lower_text = extracted_text.lower()
        
        # 1. Classify Document Type
        invoice_matches = sum(1 for k in self.invoice_keywords if k in lower_text)
        receipt_matches = sum(1 for k in self.receipt_keywords if k in lower_text)
        statement_matches = sum(1 for k in self.statement_keywords if k in lower_text)

        if invoice_matches >= 3 and invoice_matches > receipt_matches:
            evidence_type = EvidenceType.INVOICE
            payment_status = PaymentStatus.NOT_VERIFIED
            findings.append(EvidenceFinding(
                id="FIND-DOC-INVOICE-INFO",
                category="DOCUMENT_CLASSIFICATION",
                severity=FindingSeverity.INFO,
                title="Invoice Document Identified",
                description="This document appears to be an invoice or bill. An invoice represents a payment request and does NOT constitute proof that payment has completed.",
                detector="DocumentAnalysisService"
            ))
        elif statement_matches >= 3:
            evidence_type = EvidenceType.BANK_STATEMENT
            payment_status = PaymentStatus.NOT_VERIFIED
            findings.append(EvidenceFinding(
                id="FIND-DOC-STMT-INFO",
                category="DOCUMENT_CLASSIFICATION",
                severity=FindingSeverity.INFO,
                title="Bank Account Statement Identified",
                description="Parsed financial account statement entries. Individual transactions require bank reconciliation.",
                detector="DocumentAnalysisService"
            ))
        elif receipt_matches >= 2:
            evidence_type = EvidenceType.RECEIPT
            payment_status = PaymentStatus.NOT_VERIFIED
            findings.append(EvidenceFinding(
                id="FIND-DOC-RECEIPT-UNVERIFIED",
                category="SETTLEMENT_BOUNDARY",
                severity=FindingSeverity.INFO,
                title="Payment Receipt Details Extracted",
                description="Receipt details were parsed. Settlement status remains NOT_VERIFIED pending direct banking or gateway verification.",
                detector="DocumentAnalysisService"
            ))
        else:
            evidence_type = EvidenceType.GENERAL_DOCUMENT
            payment_status = PaymentStatus.NOT_APPLICABLE
            findings.append(EvidenceFinding(
                id="FIND-DOC-GENERAL-NONPAYMENT",
                category="DOCUMENT_CLASSIFICATION",
                severity=FindingSeverity.INFO,
                title="General Document (Non-Payment Context)",
                description="This file is classified as a general document. Payment verification is NOT APPLICABLE.",
                detector="DocumentAnalysisService"
            ))

        # 2. Check for Suspicious Embedded Links
        for url in extracted_urls:
            if "bit.ly" in url or "tinyurl.com" in url:
                findings.append(EvidenceFinding(
                    id="FIND-DOC-MASKED-LINK",
                    category="SUSPICIOUS_LINK",
                    severity=FindingSeverity.MEDIUM,
                    title="Shortened URL Embedded in Document",
                    description=f"Document contains masked or shortened link: {url}",
                    detector="DocumentAnalysisService",
                    evidence_excerpt=url
                ))

        return {
            "success": True,
            "evidence_type": evidence_type,
            "payment_status": payment_status,
            "findings": findings,
            "extracted_text": extracted_text[:2000],  # preview
            "extracted_urls": list(extracted_urls),
            "page_count": page_count
        }


document_service = DocumentAnalysisService()
