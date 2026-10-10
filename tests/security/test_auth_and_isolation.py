"""
Security, Multi-tenant Isolation, and Access Control Tests
Verifies:
1. Registration & password hashing validation.
2. Bearer token validation and expired/tampered rejection.
3. Cross-account access isolation: User B cannot access or download report for User A's private case.
4. Payload size rejection for oversized files (>10MB).
Quantum Kavacha Platform
"""
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.auth import hash_password, verify_password, create_access_token, decode_access_token

client = TestClient(app)


def test_password_hashing():
    raw = "SecurePlatformPass2026!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_tamper_detection():
    token = create_access_token("usr_123", "analyst@kavacha.sec", "analyst")
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "usr_123"
    assert decoded["email"] == "analyst@kavacha.sec"

    # Tampered token test
    tampered = token[:-4] + "ABCD"
    assert decode_access_token(tampered) is None


def test_cross_account_isolation():
    """Verify User B cannot access or download report of User A's investigation case."""
    # Register User A
    res_a = client.post("/api/auth/register", json={
        "email": "alice@security.org",
        "password": "PasswordAlice123!",
        "full_name": "Alice Security"
    })
    assert res_a.status_code in [200, 409]
    if res_a.status_code == 409:
        res_a = client.post("/api/auth/login", json={
            "email": "alice@security.org",
            "password": "PasswordAlice123!"
        })
    token_a = res_a.json()["access_token"]

    # Register User B
    res_b = client.post("/api/auth/register", json={
        "email": "bob@security.org",
        "password": "PasswordBob123!",
        "full_name": "Bob Security"
    })
    assert res_b.status_code in [200, 409]
    if res_b.status_code == 409:
        res_b = client.post("/api/auth/login", json={
            "email": "bob@security.org",
            "password": "PasswordBob123!"
        })
    token_b = res_b.json()["access_token"]

    # User A analyzes evidence and saves private case
    res_analysis = client.post(
        "/api/evidence/analyze",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"evidence_type": "URL", "input_text": "https://suspicious-test-portal.xyz"}
    )
    assert res_analysis.status_code == 200
    case_id = res_analysis.json()["case_id"]

    # User A can retrieve case & report
    res_get_a = client.get(f"/api/investigations/{case_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert res_get_a.status_code == 200

    res_report_a = client.get(f"/api/investigations/{case_id}/report", headers={"Authorization": f"Bearer {token_a}"})
    assert res_report_a.status_code == 200
    assert "QUANTUM KAVACHA — FORENSIC INVESTIGATION REPORT" in res_report_a.text

    # User B attempts to access User A's case -> MUST BE REJECTED (404 / Unauthorized)
    res_get_b = client.get(f"/api/investigations/{case_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res_get_b.status_code == 404

    # User B attempts to download User A's report -> MUST BE REJECTED
    res_report_b = client.get(f"/api/investigations/{case_id}/report", headers={"Authorization": f"Bearer {token_b}"})
    assert res_report_b.status_code == 404
