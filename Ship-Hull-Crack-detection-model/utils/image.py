"""
Image I/O helpers for validation, encoding, and format handling.
"""

from __future__ import annotations

import base64
import io
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def validate_image(
    file_bytes: bytes,
    filename: Optional[str] = None,
    max_size_mb: float = 20.0,
) -> Tuple[bool, str]:
    """
    Validate uploaded image bytes.

    Checks:
        - File extension (if filename provided)
        - File size
        - Image decodability

    Returns:
        (is_valid, error_message) tuple.
    """
    # Check extension
    if filename:
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"

    # Check size
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"Image too large ({size_mb:.1f} MB). Maximum: {max_size_mb} MB."

    # Check decodability
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
    except Exception as e:
        return False, f"Cannot decode image: {e}"

    return True, ""


def bytes_to_numpy(file_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to a BGR numpy array (OpenCV format)."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image bytes to numpy array.")
    return img


def encode_image_base64(img: np.ndarray, quality: int = 90) -> str:
    """
    Encode a BGR numpy array to a base64 JPEG string.

    Args:
        img: BGR numpy array from OpenCV.
        quality: JPEG quality (0-100).

    Returns:
        Base64-encoded JPEG string.
    """
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    success, buffer = cv2.imencode(".jpg", img, encode_params)
    if not success:
        raise RuntimeError("Failed to encode image to JPEG.")
    return base64.b64encode(buffer).decode("utf-8")
