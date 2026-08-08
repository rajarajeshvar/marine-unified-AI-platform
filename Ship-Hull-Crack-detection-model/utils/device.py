"""
Device detection utilities.

Determines the best available compute device (CUDA, MPS, or CPU)
and reports GPU information when available.
"""

from __future__ import annotations

from typing import Dict

import torch

from utils.logger import get_logger

logger = get_logger(__name__)


def get_device(preference: str = "auto") -> str:
    """
    Resolve the compute device to use.

    Args:
        preference: One of "auto", "cpu", "0", "1", etc.
            "auto" picks the best available device.

    Returns:
        Device string suitable for YOLO/PyTorch (e.g. "0", "cpu").
    """
    if preference == "cpu":
        logger.info("Device forced to CPU by configuration.")
        return "cpu"

    if preference != "auto":
        # Assume it's a GPU index like "0", "1"
        if torch.cuda.is_available():
            idx = int(preference)
            if idx < torch.cuda.device_count():
                name = torch.cuda.get_device_name(idx)
                logger.info("Using GPU %d: %s", idx, name)
                return preference
            logger.warning("GPU index %d not available. Falling back.", idx)

    # Auto-detect
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        logger.info("Auto-detected GPU: %s", name)
        return "0"

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("Auto-detected Apple MPS device.")
        return "mps"

    logger.info("No GPU detected. Using CPU.")
    return "cpu"


def get_gpu_info() -> Dict[str, str]:
    """
    Return a dictionary with GPU information.

    Returns empty values if no GPU is available.
    """
    info = {
        "gpu_available": str(torch.cuda.is_available()),
        "gpu_name": "N/A",
        "gpu_count": "0",
        "gpu_memory_mb": "N/A",
        "cuda_version": "N/A",
    }

    if torch.cuda.is_available():
        info["gpu_name"] = torch.cuda.get_device_name(0)
        info["gpu_count"] = str(torch.cuda.device_count())
        mem = torch.cuda.get_device_properties(0).total_memory
        info["gpu_memory_mb"] = f"{mem / (1024 ** 2):.0f}"
        info["cuda_version"] = torch.version.cuda or "N/A"

    return info
