"""
GPA-ERP HRIS — Face detection (simplified)

Only checks whether a human face is present in a selfie image.
No identity matching, no stored embeddings, no registration step required.

Usage:
    from app.hris_face import detect_face

    face_found, confidence = detect_face(image_bytes)
    # face_found   : bool  — True if at least one face detected
    # confidence   : float — detection confidence 0.0–1.0 (0.0 if no face / unavailable)
"""
from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

# deepface is an optional dependency — gracefully degrade if not installed
try:
    import numpy as np
    from deepface import DeepFace
    _DEEPFACE_AVAILABLE = True
except ImportError:
    _DEEPFACE_AVAILABLE = False
    logger.warning(
        "deepface not installed — face detection disabled (clock-in still allowed). "
        "Run: pip install deepface"
    )

# opencv-only detector: lightweight, no extra model download required
_DETECTOR = "opencv"
# Minimum confidence to count a detection as a real face (reduces false positives)
_MIN_CONFIDENCE = 0.5


def _bytes_to_array(image_bytes: bytes):
    """Convert raw image bytes → numpy array (RGB)."""
    import numpy as np
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(img)


def detect_face(image_bytes: bytes) -> tuple[bool, float]:
    """
    Detect whether at least one face is present in the image.

    Returns:
        (face_found: bool, confidence: float 0.0–1.0)

    If deepface is not installed, returns (False, 0.0) — clock-in proceeds
    without face validation and `face_verified` stays False on the record.
    """
    if not _DEEPFACE_AVAILABLE:
        logger.debug("deepface unavailable — skipping face detection")
        return False, 0.0

    try:
        img_array = _bytes_to_array(image_bytes)
        # extract_faces returns a list of dicts with keys: face, facial_area, confidence
        # enforce_detection=False means no exception if no face found
        faces = DeepFace.extract_faces(
            img_path          = img_array,
            detector_backend  = _DETECTOR,
            enforce_detection = False,
            align             = False,   # skip alignment for speed
        )

        # Filter to confident detections only
        valid = [f for f in faces if f.get("confidence", 0) >= _MIN_CONFIDENCE]

        if not valid:
            return False, 0.0

        best_confidence = max(f.get("confidence", 0.0) for f in valid)
        return True, round(float(best_confidence), 3)

    except Exception as exc:
        logger.warning("Face detection error: %s", exc)
        return False, 0.0
