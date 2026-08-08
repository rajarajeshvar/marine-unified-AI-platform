"""
Model evaluation module.

Computes and exports metrics (Precision, Recall, mAP) and extracts
training curves from YOLO run artifacts.
"""

from __future__ import annotations

import json
import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ultralytics import YOLO

from config.settings import AppConfig, get_config
from utils.device import get_device, get_gpu_info
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    """Structured evaluation output."""

    precision: float = 0.0
    recall: float = 0.0
    map50: float = 0.0
    map50_95: float = 0.0
    f1: float = 0.0
    per_class: Dict[str, Dict[str, float]] = field(default_factory=dict)
    model_info: Dict[str, Any] = field(default_factory=dict)
    raw_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "mAP@50": round(self.map50, 4),
            "mAP@50-95": round(self.map50_95, 4),
            "f1_score": round(self.f1, 4),
            "per_class": self.per_class,
            "model_info": self.model_info,
        }


class ModelEvaluator:
    """
    Evaluate a trained YOLOv8 model on a dataset split.

    Usage:
        evaluator = ModelEvaluator(weights_path="runs/crack_detect/weights/best.pt")
        result = evaluator.evaluate(split="test")
        evaluator.export_report("runs/crack_detect/evaluation.json")
    """

    def __init__(
        self,
        weights_path: str,
        config: Optional[AppConfig] = None,
    ) -> None:
        self.config = config or get_config()
        self.weights_path = Path(weights_path)
        self.model: Optional[YOLO] = None
        self.device: str = "cpu"
        self._last_result: Optional[EvaluationResult] = None

        if not self.weights_path.exists():
            raise FileNotFoundError(f"Model weights not found: {self.weights_path}")

    def setup(self) -> None:
        """Load the model and resolve compute device."""
        self.device = get_device(self.config.inference.device)
        self.model = YOLO(str(self.weights_path))
        logger.info("Loaded model for evaluation: %s", self.weights_path)

    def evaluate(self, split: str = "test") -> EvaluationResult:
        """
        Run evaluation on the specified split.

        Args:
            split: "val" or "test".

        Returns:
            EvaluationResult with all metrics.
        """
        if self.model is None:
            self.setup()

        cfg = self.config
        results = self.model.val(
            data=str(cfg.dataset.data_yaml_path),
            split=split,
            imgsz=cfg.inference.image_size,
            batch=cfg.training.batch_size,
            device=self.device,
            verbose=True,
        )

        # Extract core metrics
        result = EvaluationResult()

        if hasattr(results, "results_dict"):
            rd = results.results_dict
            result.precision = rd.get("metrics/precision(B)", 0.0)
            result.recall = rd.get("metrics/recall(B)", 0.0)
            result.map50 = rd.get("metrics/mAP50(B)", 0.0)
            result.map50_95 = rd.get("metrics/mAP50-95(B)", 0.0)
            result.raw_metrics = dict(rd)

        # Compute F1
        if result.precision + result.recall > 0:
            result.f1 = 2 * (result.precision * result.recall) / (result.precision + result.recall)

        # Per-class metrics (for future multi-class support)
        class_names = cfg.model.class_names
        if hasattr(results, "box") and hasattr(results.box, "maps"):
            for i, name in enumerate(class_names):
                if i < len(results.box.maps):
                    result.per_class[name] = {
                        "mAP@50-95": float(results.box.maps[i]),
                    }

        # Model info
        result.model_info = self.get_model_info()

        self._last_result = result
        logger.info(
            "Evaluation complete — P: %.4f  R: %.4f  mAP@50: %.4f  mAP@50-95: %.4f",
            result.precision, result.recall, result.map50, result.map50_95,
        )
        return result

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata: parameter count, size, speed."""
        if self.model is None:
            self.setup()

        info: Dict[str, Any] = {
            "variant": self.config.model.variant,
            "weights": str(self.weights_path),
            "device": self.device,
            "gpu": get_gpu_info(),
        }

        # Model file size
        if self.weights_path.exists():
            size_mb = self.weights_path.stat().st_size / (1024 * 1024)
            info["model_size_mb"] = round(size_mb, 2)

        # Parameter count from model
        if hasattr(self.model, "model") and hasattr(self.model.model, "parameters"):
            total_params = sum(p.numel() for p in self.model.model.parameters())
            info["total_parameters"] = total_params
            info["total_parameters_millions"] = round(total_params / 1e6, 2)

        return info

    @staticmethod
    def get_training_curves(run_dir: str) -> Dict[str, List[float]]:
        """
        Read training curves from results.csv in a YOLO run directory.

        Returns:
            Dict mapping column names to lists of values.
        """
        results_csv = Path(run_dir) / "results.csv"
        if not results_csv.exists():
            logger.warning("results.csv not found at %s", results_csv)
            return {}

        curves: Dict[str, List[float]] = {}
        with open(results_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key, value in row.items():
                    key = key.strip()
                    if key not in curves:
                        curves[key] = []
                    try:
                        curves[key].append(float(value.strip()))
                    except (ValueError, AttributeError):
                        curves[key].append(0.0)

        return curves

    def export_report(self, output_path: str) -> None:
        """Save the last evaluation result as a JSON file."""
        if self._last_result is None:
            logger.warning("No evaluation result to export. Run evaluate() first.")
            return

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self._last_result.to_dict(), f, indent=2, default=str)

        logger.info("Evaluation report saved: %s", out)
