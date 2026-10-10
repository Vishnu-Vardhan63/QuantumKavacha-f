"""
Authentication and Cryptographic Token Handling
Uses standard PBKDF2-HMAC-SHA256 for secure password hashing
and HMAC-SHA256 authenticated tokens with expiration.
Quantum Kavacha Platform
"""
import os
import hmac
import hashlib
import secrets
import time
import base64
import json
from typing import Optional, Dict, Any

AUTH_SECRET = os.environ.get("JWT_SECRET_KEY", "kavacha_secure_secret_default_key_2026")
TOKEN_TTL_SECONDS = 8 * 3600  # 8 hours


def hash_password(password: str) -> str:
    """Hashes password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return base64.b64encode(salt + key).decode("ascii")


def verify_password(password: str, hashed: str) -> bool:
    """Verifies password against stored PBKDF2 hash with constant-time comparison."""
    try:
        decoded = base64.b64decode(hashed.encode("ascii"))
        salt = decoded[:16]
        expected_key = decoded[16:]
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(expected_key, key)
    except Exception:
        return False


def create_access_token(user_id: str, email: str, role: str = "analyst") -> str:
    """Generates an authenticated HMAC-SHA256 signed token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
        "iat": int(time.time())
    }
    
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    msg = f"{b64_header}.{b64_payload}".encode("utf-8")
    signature = hmac.new(AUTH_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    b64_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{b64_header}.{b64_payload}.{b64_sig}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies signature and expiration of an access token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        b64_header, b64_payload, b64_sig = parts
        msg = f"{b64_header}.{b64_payload}".encode("utf-8")
        expected_sig = hmac.new(AUTH_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
        
        # Pad base64 signature
        rem = len(b64_sig) % 4
        padded_sig = b64_sig + ("=" * (4 - rem) if rem else "")
        sig_bytes = base64.urlsafe_b64decode(padded_sig.encode("ascii"))
        
        if not hmac.compare_digest(expected_sig, sig_bytes):
            return None
        
        # Decode payload
        rem_p = len(b64_payload) % 4
        padded_p = b64_payload + ("=" * (4 - rem_p) if rem_p else "")
        payload = json.loads(base64.urlsafe_b64decode(padded_p.encode("ascii")).decode("utf-8"))
        
        if payload.get("exp", 0) < int(time.time()):
            return None  # Expired
            
        return payload
    except Exception:
        return None
