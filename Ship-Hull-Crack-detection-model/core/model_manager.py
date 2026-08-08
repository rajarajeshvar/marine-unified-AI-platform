"""
Model management: loading, switching, and metadata extraction.

Provides a single interface for model lifecycle operations,
designed for future extension to ONNX/TensorRT exports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ultralytics import YOLO

from config.settings import AppConfig, get_config
from utils.device import get_device, get_gpu_info
from utils.logger import get_logger

logger = get_logger(__name__)


class ModelManager:
    """
    Manages YOLO model lifecycle: loading, switching, and info extraction.

    Usage:
        manager = ModelManager()
        manager.load("runs/crack_detect/weights/best.pt")
        info = manager.get_info()
        manager.switch_variant("yolov8s")
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or get_config()
        self.model: Optional[YOLO] = None
        self.current_weights: Optional[str] = None
        self.current_variant: str = self.config.model.variant
        self.device: str = "cpu"

    def load(self, weights_path: Optional[str] = None) -> None:
        """
        Load a model from weights.

        Args:
            weights_path: Path to .pt file. Defaults to config inference weights.
        """
        wp = weights_path or str(self.config.inference.weights_path)
        p = Path(wp)

        if not p.exists():
            raise FileNotFoundError(f"Weights not found: {p}")

        self.device = get_device(self.config.inference.device)
        self.model = YOLO(str(p))
        self.current_weights = str(p)
        logger.info("Model loaded: %s on device %s", p.name, self.device)

    def switch_variant(self, variant: str) -> None:
        """
        Switch to a different YOLO variant (downloads pretrained if needed).

        Args:
            variant: e.g. "yolov8n", "yolov8s", "yolov8m", "yolov8l"
        """
        self.device = get_device(self.config.inference.device)
        self.model = YOLO(f"{variant}.pt")
        self.current_variant = variant
        self.current_weights = f"{variant}.pt"
        logger.info("Switched to variant: %s", variant)

    def get_info(self) -> Dict[str, Any]:
        """
        Return model metadata.

        Includes: variant, weights path, parameter count, model size,
        device, GPU info, class names.
        """
        info: Dict[str, Any] = {
            "variant": self.current_variant,
            "weights": self.current_weights,
            "device": self.device,
            "loaded": self.model is not None,
            "class_names": self.config.model.class_names,
            "num_classes": self.config.model.num_classes,
            "gpu": get_gpu_info(),
        }

        if self.current_weights:
            p = Path(self.current_weights)
            if p.exists():
                info["model_size_mb"] = round(p.stat().st_size / (1024 * 1024), 2)

        if self.model and hasattr(self.model, "model"):
            try:
                params = sum(p.numel() for p in self.model.model.parameters())
                info["total_parameters"] = params
                info["total_parameters_millions"] = round(params / 1e6, 2)
            except Exception:
                pass

        return info

    @property
    def is_loaded(self) -> bool:
        return self.model is not None
