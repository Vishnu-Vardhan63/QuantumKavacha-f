"""
In-Memory & SQLite Case Persistence & User Authentication Store
Quantum Kavacha Platform
"""
import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from apps.api.schemas import EvidenceAnalysisResult

DB_PATH = os.path.join(os.path.dirname(__file__), "kavacha_cases.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            final_verdict TEXT NOT NULL,
            risk_score REAL,
            summary TEXT,
            result_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_case(result: EvidenceAnalysisResult):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO cases (case_id, created_at, evidence_type, final_verdict, risk_score, summary, result_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        result.case_id,
        result.created_at,
        result.evidence_type.value,
        result.final_verdict.value,
        result.risk_score,
        result.summary,
        result.model_dump_json()
    ))
    conn.commit()
    conn.close()


def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT result_json FROM cases WHERE case_id = ?", (case_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None


def list_cases(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT case_id, created_at, evidence_type, final_verdict, risk_score, summary 
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
            "summary": r[5]
        }
        for r in rows
    ]
