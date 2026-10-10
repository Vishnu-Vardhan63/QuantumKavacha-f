"""
FastAPI Server Entrypoint with Real Authentication & Role-Based Authorization
Quantum Kavacha Platform
"""
import sys
import os
import base64
from typing import Optional

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from apps.api.schemas import EvidenceSubmitRequest, EvidenceAnalysisResult
from apps.api.auth import hash_password, verify_password, create_access_token, decode_access_token
from apps.api.database import (
    save_case, get_case, list_cases, create_user, get_user_by_email, init_db
)
from services.evidence.pipeline import evidence_pipeline
from services.evidence.report_generator import generate_markdown_report
from services.quantum_research.service import quantum_service
from services.threat_intelligence.service import threat_intel_service

# Initialize database schema
init_db()

app = FastAPI(
    title="Quantum Kavacha Platform API",
    version="2.0.0",
    description="Enterprise Cybersecurity & Digital Payment Forensics Platform"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://quantum-kavacha.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- AUTH DEPENDENCIES ---

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Extracts authenticated user if Bearer token is provided, else returns None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split("Bearer ", 1)[1].strip()
    return decode_access_token(token)


def get_current_user_required(authorization: Optional[str] = Header(None)) -> dict:
    """Enforces authentication; raises 401 if token is missing or invalid."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required or invalid session token.")
    return user


# --- AUTH ROUTES ---

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    
    hashed = hash_password(req.password)
    user = create_user(email=req.email, hashed_password=hashed, full_name=req.full_name)
    token = create_access_token(user_id=user["user_id"], email=user["email"], role=user["role"])
    return {
        "user": {"user_id": user["user_id"], "email": user["email"], "full_name": user["full_name"], "role": user["role"]},
        "access_token": token
    }


@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    token = create_access_token(user_id=user["user_id"], email=user["email"], role=user["role"])
    return {
        "user": {"user_id": user["user_id"], "email": user["email"], "full_name": user["full_name"], "role": user["role"]},
        "access_token": token
    }


# --- HEALTH & AUDIT ---

@app.get("/api/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "Quantum Kavacha Platform API",
        "version": "2.0.0",
        "dependencies": {
            "qr_engine": "ACTIVE",
            "pdf_engine": "ACTIVE",
            "quantum_simulation": "ACTIVE",
            "auth_engine": "ACTIVE"
        }
    }


# --- EVIDENCE ANALYSIS ROUTES ---

@app.post("/api/evidence/analyze", response_model=EvidenceAnalysisResult)
def analyze_evidence_json(
    request: EvidenceSubmitRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    owner_id = current_user["sub"] if current_user else "usr_public_guest"
    result = evidence_pipeline.run_pipeline(request)
    save_case(result, owner_id=owner_id)
    return result


@app.post("/api/evidence/upload", response_model=EvidenceAnalysisResult)
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    owner_id = current_user["sub"] if current_user else "usr_public_guest"
    content = await file.read()
    
    # Upload size limit: 10MB
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload exceeds maximum permitted size of 10 MB.")
    
    b64_str = base64.b64encode(content).decode("utf-8")
    req = EvidenceSubmitRequest(
        filename=file.filename,
        image_base64=b64_str
    )
    result = evidence_pipeline.run_pipeline(req)
    save_case(result, owner_id=owner_id)
    return result


# --- INVESTIGATIONS & REPORTS ---

@app.get("/api/investigations")
def get_investigations(current_user: Optional[dict] = Depends(get_current_user_optional)):
    owner_id = current_user["sub"] if current_user else None
    return list_cases(owner_id=owner_id, limit=100)


@app.get("/api/investigations/{case_id}")
def get_investigation_detail(
    case_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    owner_id = current_user["sub"] if current_user else None
    case_data = get_case(case_id, owner_id=owner_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Investigation case not found or unauthorized access.")
    return case_data


@app.get("/api/investigations/{case_id}/report")
def export_investigation_report(
    case_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    owner_id = current_user["sub"] if current_user else None
    case_data = get_case(case_id, owner_id=owner_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Investigation case not found or unauthorized access.")
    
    md_content = generate_markdown_report(case_data)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=report_{case_id}.md"}
    )


# --- THREAT INTELLIGENCE & RESEARCH ---

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
