"""
Canonical Pydantic Schemas matching packages/contracts/evidence.ts
Quantum Kavacha Platform
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class EvidenceType(str, Enum):
    QR_CODE = "QR_CODE"
    URL = "URL"
    PAYMENT_SCREENSHOT = "PAYMENT_SCREENSHOT"
    RECEIPT = "RECEIPT"
    INVOICE = "INVOICE"
    TRANSACTION_RECORD = "TRANSACTION_RECORD"
    BANK_STATEMENT = "BANK_STATEMENT"
    GENERAL_DOCUMENT = "GENERAL_DOCUMENT"
    IMAGE = "IMAGE"
    UNKNOWN = "UNKNOWN"


class Verdict(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    INCONCLUSIVE = "INCONCLUSIVE"


class AnalysisStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class PaymentStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class FindingSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceFinding(BaseModel):
    id: str
    category: str
    severity: FindingSeverity
    title: str
    description: str
    detector: str
    evidence_excerpt: Optional[str] = None
    confidence: Optional[float] = None


class ModelStatus(BaseModel):
    detector_name: str
    status: str = Field(description="EXECUTED, SKIPPED, UNAVAILABLE, or FAILED")
    latency_ms: float = 0.0
    details: Optional[str] = None


class ExtractedEntities(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[str] = None
    recipient_vpa: Optional[str] = None
    sender_vpa: Optional[str] = None
    raw_qr_payload: Optional[str] = None
    destination_url: Optional[str] = None
    document_type: Optional[str] = None


class EvidenceAnalysisResult(BaseModel):
    case_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_type: EvidenceType
    transaction_detected: Optional[bool] = None
    final_verdict: Verdict
    risk_score: Optional[float] = None  # 0.0 - 100.0
    confidence: Optional[float] = None  # 0.0 - 1.0
    reason_codes: List[str] = Field(default_factory=list)
    summary: str
    evidence_findings: List[EvidenceFinding] = Field(default_factory=list)
    extracted_entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    model_status: Dict[str, ModelStatus] = Field(default_factory=dict)
    analysis_status: AnalysisStatus
    payment_status: PaymentStatus
    limitations: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class EvidenceSubmitRequest(BaseModel):
    evidence_type: Optional[EvidenceType] = None
    input_text: Optional[str] = None
    image_base64: Optional[str] = None
    filename: Optional[str] = None
    declared_amount: Optional[float] = None
    declared_vpa: Optional[str] = None
