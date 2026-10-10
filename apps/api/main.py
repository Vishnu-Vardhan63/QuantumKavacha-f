"""
FastAPI Server Entrypoint
Quantum Kavacha Platform
"""
import sys
import os
# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from apps.api.schemas import EvidenceSubmitRequest, EvidenceAnalysisResult
from services.evidence.pipeline import evidence_pipeline
from services.quantum_research.service import quantum_service
from services.threat_intelligence.service import threat_intel_service
from apps.api.database import save_case, get_case, list_cases

app = FastAPI(
    title="Quantum Kavacha Platform API",
    version="2.0.0",
    description="Enterprise Cybersecurity & Digital Payment Forensics Platform"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "Quantum Kavacha Platform API",
        "version": "2.0.0",
        "dependencies": {
            "qr_engine": "ACTIVE",
            "pdf_engine": "ACTIVE",
            "quantum_simulation": "ACTIVE"
        }
    }


@app.post("/api/evidence/analyze", response_model=EvidenceAnalysisResult)
def analyze_evidence_json(request: EvidenceSubmitRequest):
    result = evidence_pipeline.run_pipeline(request)
    save_case(result)
    return result


@app.post("/api/evidence/upload", response_model=EvidenceAnalysisResult)
async def upload_evidence(file: UploadFile = File(...)):
    import base64
    content = await file.read()
    b64_str = base64.b64encode(content).decode("utf-8")
    
    req = EvidenceSubmitRequest(
        filename=file.filename,
        image_base64=b64_str
    )
    result = evidence_pipeline.run_pipeline(req)
    save_case(result)
    return result


@app.get("/api/investigations")
def get_investigations():
    return list_cases(limit=100)


@app.get("/api/investigations/{case_id}")
def get_investigation_detail(case_id: str):
    case_data = get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Investigation case not found")
    return case_data


@app.get("/api/threat-intel/indicators")
def get_threat_indicators():
    return [
        {
            "indicator": "paytm-cashback-reward.xyz",
            "type": "DOMAIN",
            "severity": "CRITICAL",
            "category": "BRAND_IMPERSONATION",
            "first_seen": "2026-10-09T08:00:00Z",
            "status": "CONFIRMED_MALICIOUS"
        },
        {
            "indicator": "upi://pay?pa=refund-desk@ybl&pn=QuickSupport",
            "type": "UPI_URI",
            "severity": "HIGH",
            "category": "SOCIAL_ENGINEERING",
            "first_seen": "2026-10-10T02:15:00Z",
            "status": "SUSPICIOUS"
        },
        {
            "indicator": "194.26.29.112",
            "type": "IP_HOST",
            "severity": "HIGH",
            "category": "C2_INFRASTRUCTURE",
            "first_seen": "2026-10-08T14:30:00Z",
            "status": "CONFIRMED_MALICIOUS"
        }
    ]


@app.get("/api/quantum/benchmark")
def get_quantum_benchmark():
    return quantum_service.run_benchmark()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=True)
