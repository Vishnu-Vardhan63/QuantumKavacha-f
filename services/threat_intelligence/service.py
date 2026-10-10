"""
Threat Intelligence & URL Analysis Service
Handles URL normalization, suspicious domain structure, typosquatting indicators,
and domain entropy.
Quantum Kavacha Platform
"""
import math
import re
import urllib.parse
from typing import Dict, Any, List, Optional
from apps.api.schemas import EvidenceFinding, FindingSeverity, ModelStatus


def calculate_entropy(text: str) -> float:
    """Calculates Shannon entropy for domain randomness detection."""
    if not text:
        return 0.0
    entropy = 0.0
    for char in set(text):
        p = text.count(char) / len(text)
        entropy -= p * math.log2(p)
    return entropy


class ThreatIntelligenceService:
    def __init__(self):
        # Known financial domains for brand-jacking checks
        self.popular_brands = [
            "google", "paytm", "phonepe", "amazon", "apple", "microsoft",
            "paypal", "sbi", "hdfc", "icici", "axisbank", "razorpay"
        ]

    def analyze_url(self, raw_url: str) -> Dict[str, Any]:
        """
        Parses and inspects URL structure, domains, and flags suspicious patterns.
        """
        findings: List[EvidenceFinding] = []
        url = raw_url.strip()
        
        # Ensure scheme for proper urlparse
        if not (url.startswith("http://") or url.startswith("https://")):
            url_to_parse = "http://" + url
        else:
            url_to_parse = url

        try:
            parsed = urllib.parse.urlparse(url_to_parse)
            netloc = parsed.netloc.lower()
            # Strip port if present
            host = netloc.split(":")[0]
        except Exception:
            findings.append(EvidenceFinding(
                id="FIND-URL-MALFORMED",
                category="SYNTAX_VALIDATION",
                severity=FindingSeverity.HIGH,
                title="Malformed URL Syntax",
                description="Unable to parse URL components safely.",
                detector="ThreatIntelligenceService",
                evidence_excerpt=raw_url[:60]
            ))
            return {
                "url": raw_url,
                "findings": findings,
                "risk_score": 75.0,
                "entropy": 0.0
            }

        # 1. Shannon Entropy (Random DGA domains)
        domain_entropy = calculate_entropy(host)
        if domain_entropy > 4.2 and len(host) > 14:
            findings.append(EvidenceFinding(
                id="FIND-URL-HIGH-ENTROPY",
                category="DOMAIN_ANOMALY",
                severity=FindingSeverity.MEDIUM,
                title="High Domain Name Entropy",
                description=f"Host '{host}' exhibits high character randomness ({domain_entropy:.2f}), a common trait of algorithmically generated scam domains.",
                detector="ThreatIntelligenceService",
                evidence_excerpt=host
            ))

        # 2. Typosquatting / Brand Spoofing Check
        # e.g., 'paytm-reward.xyz', 'support-hdfc.com', 'secure-phonepe-help.online'
        for brand in self.popular_brands:
            if brand in host and not host.endswith(f".{brand}.com") and host != f"{brand}.com" and not host.endswith(f".{brand}.in") and host != f"{brand}.in":
                # Check if it has suspicious prefixes or suffixes
                if any(x in host for x in ["-", "_", "login", "verify", "support", "secure", "bonus", "reward", "cash"]):
                    findings.append(EvidenceFinding(
                        id="FIND-URL-BRAND-SPOOF",
                        category="PHISHING_INDICATOR",
                        severity=FindingSeverity.HIGH,
                        title=f"Potential Brand Impersonation: {brand.upper()}",
                        description=f"Host '{host}' incorporates the legitimate brand '{brand}' with suspicious subdomains or hyphens.",
                        detector="ThreatIntelligenceService",
                        evidence_excerpt=host
                    ))

        # 3. Suspicious TLD check
        suspicious_tlds = [".xyz", ".top", ".buzz", ".work", ".click", ".link", ".loan", ".club", ".monster"]
        for tld in suspicious_tlds:
            if host.endswith(tld):
                findings.append(EvidenceFinding(
                    id="FIND-URL-SUS-TLD",
                    category="REPUTATION_INDICATOR",
                    severity=FindingSeverity.LOW,
                    title="High-Risk Top Level Domain (TLD)",
                    description=f"The domain uses '{tld}', an inexpensive TLD statistically associated with disposable phishing campaigns.",
                    detector="ThreatIntelligenceService",
                    evidence_excerpt=host
                ))
                break

        # 4. Dangerous File Extension in Path
        path = parsed.path.lower()
        dangerous_exts = [".apk", ".exe", ".scr", ".bat", ".vbs", ".cmd", ".iso"]
        for ext in dangerous_exts:
            if path.endswith(ext):
                findings.append(EvidenceFinding(
                    id="FIND-URL-MALICIOUS-PAYLOAD",
                    category="PAYLOAD_DOWNLOAD",
                    severity=FindingSeverity.CRITICAL,
                    title="Direct Executable / Malware Download",
                    description=f"URL path directly links to an executable payload ('{ext}').",
                    detector="ThreatIntelligenceService",
                    evidence_excerpt=path
                ))
                break

        # Calculate preliminary risk score
        risk_score = 0.0
        for f in findings:
            if f.severity == FindingSeverity.CRITICAL:
                risk_score = max(risk_score, 90.0)
            elif f.severity == FindingSeverity.HIGH:
                risk_score = max(risk_score, 70.0)
            elif f.severity == FindingSeverity.MEDIUM:
                risk_score = max(risk_score, 45.0)
            elif f.severity == FindingSeverity.LOW:
                risk_score = max(risk_score, 20.0)

        return {
            "url": raw_url,
            "host": host,
            "findings": findings,
            "risk_score": risk_score,
            "entropy": domain_entropy
        }


threat_intel_service = ThreatIntelligenceService()
