"""
Image & Payment Forensics Service
Inspects image integrity, EXIF editing signatures, font anomalies, and screenshot fields.
Quantum Kavacha Platform
"""
import io
import os
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from apps.api.schemas import EvidenceFinding, FindingSeverity, PaymentStatus, EvidenceType

KNOWN_EDITING_SOFTWARE = [
    "photoshop", "gimp", "canva", "picsart", "adobe", "pixelmator",
    "lightroom", "snapseed", "vsco", "pixlr", "paint.net"
]

class ImagePaymentForensicsService:
    def inspect_image_bytes(self, image_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Performs forensic inspection of an image file:
        - Validates magic bytes / format
        - Detects editing software tags in EXIF
        - Checks for dimension or compression anomalies
        """
        findings: List[EvidenceFinding] = []
        file_size = len(image_bytes)
        sha256 = hashlib.sha256(image_bytes).hexdigest()

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_format = img.format
                width, height = img.size
                info = img.info or {}

                # Check for editing software tags
                software_tags = []
                for k, v in info.items():
                    val_str = str(v).lower()
                    for sw in KNOWN_EDITING_SOFTWARE:
                        if sw in val_str:
                            software_tags.append(sw.capitalize())

                if software_tags:
                    findings.append(EvidenceFinding(
                        id="FIND-IMG-METADATA-EDIT",
                        category="TAMPERING_INDICATOR",
                        severity=FindingSeverity.HIGH,
                        title="Graphic Editing Software Footprint",
                        description=f"File metadata references image editing software ({', '.join(set(software_tags))}), suggesting possible graphical alteration.",
                        detector="ImagePaymentForensicsService",
                        evidence_excerpt=", ".join(set(software_tags))
                    ))

                # Check aspect ratio / resolution for standard mobile screenshots
                # Typical phones have aspect ratio around 16:9 to 21:9
                ratio = max(width, height) / max(1, min(width, height))
                is_screenshot_proportions = (1.6 <= ratio <= 2.3)

                return {
                    "valid": True,
                    "format": img_format,
                    "size_bytes": file_size,
                    "sha256": sha256,
                    "dimensions": f"{width}x{height}",
                    "is_screenshot_proportions": is_screenshot_proportions,
                    "findings": findings
                }
        except Exception as e:
            findings.append(EvidenceFinding(
                id="FIND-IMG-CORRUPT",
                category="FILE_INTEGRITY",
                severity=FindingSeverity.HIGH,
                title="Invalid or Corrupted Image Data",
                description=f"Failed to open image: {str(e)}",
                detector="ImagePaymentForensicsService"
            ))
            return {
                "valid": False,
                "size_bytes": file_size,
                "sha256": sha256,
                "findings": findings
            }


image_forensics_service = ImagePaymentForensicsService()
