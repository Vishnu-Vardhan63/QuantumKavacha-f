"""
QR Analysis Service - Robust QR decoding and URI/payload inspection
Quantum Kavacha Platform
"""
import urllib.parse
import re
from typing import Dict, Any, Tuple, Optional, List
import cv2
import numpy as np
from apps.api.schemas import EvidenceFinding, FindingSeverity, ModelStatus


class QRAnalysisService:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def decode_qr_bytes(self, image_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
        """
        Decodes a QR code from image bytes using OpenCV QRCodeDetector.
        Returns (decoded_payload, error_message).
        """
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None, "Unable to decode image data"
            
            val, pts, _ = self.detector.detectAndDecode(img)
            if val and len(val.strip()) > 0:
                return val.strip(), None
            
            # Secondary pass with grayscale and adaptive thresholding if needed
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            val, pts, _ = self.detector.detectAndDecode(gray)
            if val and len(val.strip()) > 0:
                return val.strip(), None
                
            return None, "No readable QR code found in the image"
        except Exception as e:
            return None, f"QR decoding error: {str(e)}"

    def parse_payload(self, raw_text: str) -> Dict[str, Any]:
        """
        Parses UPI URIs, HTTP(S) links, or arbitrary strings.
        """
        text = raw_text.strip()
        result: Dict[str, Any] = {
            "raw_payload": text,
            "scheme": None,
            "is_upi": False,
            "is_url": False,
            "upi_params": {},
            "url_components": {}
        }

        if text.lower().startswith("upi://pay"):
            result["is_upi"] = True
            result["scheme"] = "upi"
            try:
                parsed = urllib.parse.urlparse(text)
                params = urllib.parse.parse_qs(parsed.query)
                result["upi_params"] = {k: v[0] for k, v in params.items()}
            except Exception:
                pass
        elif text.lower().startswith("http://") or text.lower().startswith("https://"):
            result["is_url"] = True
            result["scheme"] = "https" if text.lower().startswith("https://") else "http"
            try:
                parsed = urllib.parse.urlparse(text)
                result["url_components"] = {
                    "scheme": parsed.scheme,
                    "netloc": parsed.netloc,
                    "path": parsed.path,
                    "query": parsed.query
                }
            except Exception:
                pass
        return result

    def inspect_payload(self, parsed: Dict[str, Any]) -> List[EvidenceFinding]:
        """
        Analyzes decoded payload for indicators of deception, spoofing, or policy anomalies.
        """
        findings: List[EvidenceFinding] = []
        raw = parsed.get("raw_payload", "")

        # 1. Plain HTTP Check
        if parsed.get("scheme") == "http":
            findings.append(EvidenceFinding(
                id="FIND-QR-HTTP-01",
                category="TRANSPORT_SECURITY",
                severity=FindingSeverity.HIGH,
                title="Insecure HTTP Destination",
                description="The QR code points to an unencrypted HTTP destination, susceptible to man-in-the-middle attacks.",
                detector="QRAnalysisService",
                evidence_excerpt=raw[:80]
            ))

        # 2. UPI Scheme Inspection
        if parsed.get("is_upi"):
            upi = parsed.get("upi_params", {})
            pa = upi.get("pa", "")
            pn = upi.get("pn", "")
            
            if not pa:
                findings.append(EvidenceFinding(
                    id="FIND-QR-UPI-NOPAYEE",
                    category="PAYMENT_STRUCTURE",
                    severity=FindingSeverity.HIGH,
                    title="Missing Payee Address (pa)",
                    description="The UPI payload lacks the mandatory Payee VPA address ('pa' parameter).",
                    detector="QRAnalysisService"
                ))
            else:
                # Check for deceptive handles (e.g., looks like bank support or refund scam)
                lower_pa = pa.lower()
                sus_keywords = ["refund", "helpline", "tollfree", "cashback", "customer-care", "kyc-update"]
                matched = [kw for kw in sus_keywords if kw in lower_pa]
                if matched:
                    findings.append(EvidenceFinding(
                        id="FIND-QR-UPI-SUS-HANDLE",
                        category="SOCIAL_ENGINEERING",
                        severity=FindingSeverity.MEDIUM,
                        title="Suspicious Payee Handle Pattern",
                        description=f"Payee VPA contains social engineering keywords ({', '.join(matched)}), commonly used in scam QR codes.",
                        detector="QRAnalysisService",
                        evidence_excerpt=pa
                    ))

        # 3. URL Destination Inspection
        if parsed.get("is_url"):
            url_comp = parsed.get("url_components", {})
            netloc = url_comp.get("netloc", "").lower()
            
            # Check for IP address as netloc
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", netloc):
                findings.append(EvidenceFinding(
                    id="FIND-QR-URL-RAWIP",
                    category="SUSPICIOUS_DESTINATION",
                    severity=FindingSeverity.HIGH,
                    title="Direct IP Address Host",
                    description="The destination URL uses a raw IP address instead of a registered domain name.",
                    detector="QRAnalysisService",
                    evidence_excerpt=netloc
                ))

            # Check for URL shorteners
            shorteners = ["bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "cutt.ly"]
            if any(netloc == s or netloc.endswith("." + s) for s in shorteners):
                findings.append(EvidenceFinding(
                    id="FIND-QR-URL-SHORTENER",
                    category="EVASION_TECHNIQUE",
                    severity=FindingSeverity.MEDIUM,
                    title="URL Shortener Detected",
                    description="The QR code uses a URL shortening service that masks the final destination.",
                    detector="QRAnalysisService",
                    evidence_excerpt=netloc
                ))

        return findings


qr_service = QRAnalysisService()
