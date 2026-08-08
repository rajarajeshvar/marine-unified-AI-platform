"""
CLI entry point for training the crack detection model.

Usage:
    python scripts/train.py
    python scripts/train.py --epochs 100 --model yolov8s --batch-size 32
    python scripts/train.py --config config/default.yaml --resume
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import AppConfig, get_config
from core.trainer import CrackTrainer
from utils.logger import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 crack detection model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file")
    parser.add_argument("--model", type=str, default=None, help="YOLO variant (yolov8n, yolov8s, etc.)")
    parser.add_argument("--epochs", type=int, default=None, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument("--image-size", type=int, default=None, help="Input image size")
    parser.add_argument("--lr", type=float, default=None, help="Initial learning rate")
    parser.add_argument("--device", type=str, default=None, help="Device: auto, 0, cpu")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--weights", type=str, default=None, help="Path to pretrained weights")
    parser.add_argument("--name", type=str, default=None, help="Run name")
    return parser.parse_args()


def main() -> None:
    setup_logging(log_file=PROJECT_ROOT / "runs" / "training.log")
    logger = get_logger("train")

    args = parse_args()
    config = get_config(args.config)

    # Apply CLI overrides
    if args.model:
        config.model.variant = args.model
    if args.epochs is not None:
        config.training.epochs = args.epochs
    if args.batch_size is not None:
        config.training.batch_size = args.batch_size
    if args.image_size is not None:
        config.training.image_size = args.image_size
    if args.lr is not None:
        config.training.learning_rate = args.lr
    if args.device:
        config.training.device = args.device
    if args.resume:
        config.training.resume = True
    if args.weights:
        config.model.weights = args.weights
    if args.name:
        config.training.name = args.name

    logger.info("=" * 60)
    logger.info("CRACK DETECTION — TRAINING")
    logger.info("=" * 60)
    logger.info("Model variant : %s", config.model.variant)
    logger.info("Epochs        : %d", config.training.epochs)
    logger.info("Batch size    : %d", config.training.batch_size)
    logger.info("Image size    : %d", config.training.image_size)
    logger.info("Learning rate : %.4f", config.training.learning_rate)
    logger.info("Device        : %s", config.training.device)
    logger.info("Resume        : %s", config.training.resume)
    logger.info("=" * 60)

    trainer = CrackTrainer(config)
    result = trainer.train()

    logger.info("")
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)

    if result.success:
        logger.info("Status        : SUCCESS")
        logger.info("Best weights  : %s", result.best_weights)
        logger.info("Last weights  : %s", result.last_weights)
        logger.info("Time          : %.1f seconds (%.1f min)", result.training_time_seconds, result.training_time_seconds / 60)
        logger.info("Device        : %s", result.device_used)
        if result.metrics:
            logger.info("--- Metrics ---")
            for k, v in result.metrics.items():
                if isinstance(v, float):
                    logger.info("  %s: %.4f", k, v)
    else:
        logger.error("Status        : FAILED")
        logger.error("Error         : %s", result.error)
        sys.exit(1)


if __name__ == "__main__":
    main()
