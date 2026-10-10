"""
In-Memory & SQLite Case Persistence & User Authentication Store
Quantum Kavacha Platform
"""
import sqlite3
import json
import os
import uuid
from typing import List, Optional, Dict, Any
from apps.api.schemas import EvidenceAnalysisResult

DB_PATH = os.path.join(os.path.dirname(__file__), "kavacha_cases.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Cases table with explicit owner_id
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            final_verdict TEXT NOT NULL,
            risk_score REAL,
            summary TEXT,
            result_json TEXT NOT NULL
        )
    """)
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_case(result: EvidenceAnalysisResult, owner_id: str = "usr_analyst_default"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO cases (case_id, owner_id, created_at, evidence_type, final_verdict, risk_score, summary, result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result.case_id,
        owner_id,
        result.created_at,
        result.evidence_type.value,
        result.final_verdict.value,
        result.risk_score,
        result.summary,
        result.model_dump_json()
    ))
    conn.commit()
    conn.close()


def get_case(case_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if owner_id:
        cur.execute("SELECT result_json, owner_id FROM cases WHERE case_id = ? AND owner_id = ?", (case_id, owner_id))
    else:
        cur.execute("SELECT result_json, owner_id FROM cases WHERE case_id = ?", (case_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        data = json.loads(row[0])
        data["owner_id"] = row[1]
        return data
    return None


def list_cases(owner_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if owner_id:
        cur.execute("""
            SELECT case_id, created_at, evidence_type, final_verdict, risk_score, summary, owner_id
            FROM cases WHERE owner_id = ? ORDER BY created_at DESC LIMIT ?
        """, (owner_id, limit))
    else:
        cur.execute("""
            SELECT case_id, created_at, evidence_type, final_verdict, risk_score, summary, owner_id
            FROM cases ORDER BY created_at DESC LIMIT ?
        """, (limit,))
    rows = cur.fetchall()
    conn.close()
    
    return [
        {
            "case_id": r[0],
            "created_at": r[1],
            "evidence_type": r[2],
            "final_verdict": r[3],
            "risk_score": r[4],
            "summary": r[5],
            "owner_id": r[6]
        }
        for r in rows
    ]


def create_user(email: str, hashed_password: str, full_name: str, role: str = "analyst") -> Dict[str, Any]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    import datetime
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cur.execute("""
        INSERT INTO users (user_id, email, hashed_password, full_name, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, email.lower(), hashed_password, full_name, role, created_at))
    conn.commit()
    conn.close()
    return {"user_id": user_id, "email": email.lower(), "full_name": full_name, "role": role}


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, email, hashed_password, full_name, role FROM users WHERE email = ?", (email.lower(),))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "full_name": row[3],
            "role": row[4]
        }
    return None
