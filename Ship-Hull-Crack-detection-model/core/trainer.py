"""
Training pipeline for YOLOv8 crack detection.

Handles model initialization, training execution, checkpoint saving,
and resume-from-checkpoint functionality.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from ultralytics import YOLO

from config.settings import AppConfig, get_config
from utils.device import get_device, get_gpu_info
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrainingResult:
    """Structured output from a training run."""

    success: bool
    model_path: Optional[str] = None
    best_weights: Optional[str] = None
    last_weights: Optional[str] = None
    epochs_completed: int = 0
    training_time_seconds: float = 0.0
    device_used: str = "cpu"
    gpu_info: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class CrackTrainer:
    """
    YOLOv8 training pipeline for crack detection.

    Usage:
        trainer = CrackTrainer()          # Uses default config
        trainer = CrackTrainer(config)    # Uses custom config
        result = trainer.train()
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or get_config()
        self.model: Optional[YOLO] = None
        self.device: str = "cpu"

    def setup(self) -> None:
        """
        Initialize the model and resolve the compute device.

        Validates that the dataset exists and data.yaml is accessible.
        """
        cfg = self.config

        # Validate dataset
        data_yaml = cfg.dataset.data_yaml_path
        if not data_yaml.exists():
            raise FileNotFoundError(
                f"Dataset config not found: {data_yaml}\n"
                f"Expected dataset at: {cfg.dataset.root_path}"
            )
        logger.info("Dataset config found: %s", data_yaml)

        # Resolve device
        self.device = get_device(cfg.training.device)
        logger.info("Using device: %s", self.device)

        # Load model
        if cfg.training.resume and cfg.training.resume_weights_path:
            weights = str(cfg.training.resume_weights_path)
            logger.info("Resuming from checkpoint: %s", weights)
        elif cfg.model.weights_path:
            weights = str(cfg.model.weights_path)
            logger.info("Loading custom weights: %s", weights)
        else:
            weights = f"{cfg.model.variant}.pt"
            logger.info("Using pretrained %s weights.", cfg.model.variant)

        self.model = YOLO(weights)
        logger.info("Model loaded: %s", weights)

    def train(self) -> TrainingResult:
        """
        Run the full training pipeline.

        Returns:
            TrainingResult with paths, timing, and metrics.
        """
        if self.model is None:
            self.setup()

        cfg = self.config
        start_time = time.time()

        try:
            results = self.model.train(
                data=str(cfg.dataset.data_yaml_path),
                epochs=cfg.training.epochs,
                batch=cfg.training.batch_size,
                imgsz=cfg.training.image_size,
                lr0=cfg.training.learning_rate,
                optimizer=cfg.training.optimizer,
                patience=cfg.training.patience,
                save_period=cfg.training.save_period,
                project=str(cfg.training.project_path),
                name=cfg.training.name,
                device=self.device,
                exist_ok=True,
                resume=cfg.training.resume,
                verbose=True,
            )

            elapsed = time.time() - start_time

            # Locate saved weights
            run_dir = cfg.training.project_path / cfg.training.name
            best_pt = run_dir / "weights" / "best.pt"
            last_pt = run_dir / "weights" / "last.pt"

            # Extract metrics from results
            metrics = {}
            if results and hasattr(results, "results_dict"):
                metrics = dict(results.results_dict)

            return TrainingResult(
                success=True,
                model_path=str(run_dir),
                best_weights=str(best_pt) if best_pt.exists() else None,
                last_weights=str(last_pt) if last_pt.exists() else None,
                epochs_completed=cfg.training.epochs,
                training_time_seconds=elapsed,
                device_used=self.device,
                gpu_info=get_gpu_info(),
                metrics=metrics,
            )

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("Training failed: %s", e, exc_info=True)
            return TrainingResult(
                success=False,
                training_time_seconds=elapsed,
                device_used=self.device,
                gpu_info=get_gpu_info(),
                error=str(e),
            )

    def validate(self, split: str = "val") -> Dict[str, Any]:
        """
        Run validation on the current model.

        Args:
            split: Dataset split to validate on ("val" or "test").

        Returns:
            Dictionary of validation metrics.
        """
        if self.model is None:
            self.setup()

        cfg = self.config
        results = self.model.val(
            data=str(cfg.dataset.data_yaml_path),
            split=split,
            imgsz=cfg.training.image_size,
            batch=cfg.training.batch_size,
            device=self.device,
        )

        metrics = {}
        if hasattr(results, "results_dict"):
            metrics = dict(results.results_dict)

        return metrics
