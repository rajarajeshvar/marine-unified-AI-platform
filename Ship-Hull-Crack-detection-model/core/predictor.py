"""
Inference engine for crack detection.

Runs YOLOv8 prediction on single images and returns structured results
with bounding boxes, confidence scores, and annotated images.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
from ultralytics import YOLO

from config.settings import AppConfig, get_config
from utils.device import get_device
from utils.image import bytes_to_numpy, encode_image_base64, validate_image
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Detection:
    """A single detected object."""

    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: List[float]  # [x1, y1, x2, y2] pixel coords
    bbox_xywhn: List[float]  # [cx, cy, w, h] normalized


@dataclass
class PredictionResult:
    """Structured output from a prediction."""

    detections: List[Detection] = field(default_factory=list)
    annotated_image_base64: Optional[str] = None
    inference_time_ms: float = 0.0
    image_width: int = 0
    image_height: int = 0
    model_variant: str = ""
    num_detections: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_detections": self.num_detections,
            "detections": [
                {
                    "class_id": d.class_id,
                    "class_name": d.class_name,
                    "confidence": round(d.confidence, 4),
                    "bbox_xyxy": [round(v, 2) for v in d.bbox_xyxy],
                    "bbox_xywhn": [round(v, 4) for v in d.bbox_xywhn],
                }
                for d in self.detections
            ],
            "annotated_image_base64": self.annotated_image_base64,
            "inference_time_ms": round(self.inference_time_ms, 2),
            "image_size": {"width": self.image_width, "height": self.image_height},
            "model_variant": self.model_variant,
            "error": self.error,
        }


class CrackPredictor:
    """
    YOLOv8 inference engine for crack detection.

    Usage:
        predictor = CrackPredictor()
        result = predictor.predict("path/to/image.jpg")
        result = predictor.predict_bytes(image_bytes, "photo.jpg")
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or get_config()
        self.model: Optional[YOLO] = None
        self.device: str = "cpu"
        self._loaded_weights: Optional[str] = None

    def setup(self, weights_path: Optional[str] = None) -> None:
        """
        Load the YOLO model for inference.

        Args:
            weights_path: Override weights path. Defaults to config value.
        """
        wp = weights_path or str(self.config.inference.weights_path)
        p = Path(wp)

        if not p.exists():
            raise FileNotFoundError(
                f"Model weights not found: {p}\n"
                "Train a model first with: python scripts/train.py"
            )

        self.device = get_device(self.config.inference.device)
        self.model = YOLO(str(p))
        self._loaded_weights = str(p)
        logger.info("Predictor ready — weights: %s, device: %s", p.name, self.device)

    def predict(self, image_source: Union[str, Path, np.ndarray]) -> PredictionResult:
        """
        Run prediction on an image file path or numpy array.

        Args:
            image_source: File path string/Path, or BGR numpy array.

        Returns:
            PredictionResult with detections and annotated image.
        """
        if self.model is None:
            self.setup()

        # Load image if path
        if isinstance(image_source, (str, Path)):
            img = cv2.imread(str(image_source))
            if img is None:
                return PredictionResult(error=f"Cannot read image: {image_source}")
        else:
            img = image_source

        return self._run_inference(img)

    def predict_bytes(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
    ) -> PredictionResult:
        """
        Run prediction on raw image bytes (e.g. from an upload).

        Args:
            file_bytes: Raw image file bytes.
            filename: Original filename for format validation.

        Returns:
            PredictionResult with detections and annotated image.
        """
        # Validate
        is_valid, error_msg = validate_image(file_bytes, filename)
        if not is_valid:
            return PredictionResult(error=error_msg)

        # Decode
        try:
            img = bytes_to_numpy(file_bytes)
        except ValueError as e:
            return PredictionResult(error=str(e))

        return self._run_inference(img)

    def _run_inference(self, img: np.ndarray) -> PredictionResult:
        """Core inference logic on a BGR numpy array."""
        if self.model is None:
            self.setup()

        cfg = self.config
        h, w = img.shape[:2]

        start = time.perf_counter()
        results = self.model.predict(
            source=img,
            imgsz=cfg.inference.image_size,
            conf=cfg.inference.confidence_threshold,
            iou=cfg.inference.iou_threshold,
            device=self.device,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Parse detections
        detections: List[Detection] = []
        result_obj = results[0]  # Single image → single result

        if result_obj.boxes is not None and len(result_obj.boxes) > 0:
            boxes = result_obj.boxes
            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].cpu().numpy().tolist()
                xywhn = boxes.xywhn[i].cpu().numpy().tolist()
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                cls_name = cfg.model.class_names[cls_id] if cls_id < len(cfg.model.class_names) else f"class_{cls_id}"

                detections.append(Detection(
                    class_id=cls_id,
                    class_name=cls_name,
                    confidence=conf,
                    bbox_xyxy=xyxy,
                    bbox_xywhn=xywhn,
                ))

        # Annotated image
        annotated = result_obj.plot()
        annotated_b64 = encode_image_base64(annotated)

        return PredictionResult(
            detections=detections,
            annotated_image_base64=annotated_b64,
            inference_time_ms=elapsed_ms,
            image_width=w,
            image_height=h,
            model_variant=cfg.model.variant,
            num_detections=len(detections),
        )

    @property
    def is_loaded(self) -> bool:
        return self.model is not None
