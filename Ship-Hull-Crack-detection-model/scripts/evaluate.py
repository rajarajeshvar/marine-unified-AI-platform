"""
CLI entry point for model evaluation.

Usage:
    python scripts/evaluate.py --weights runs/crack_detect/weights/best.pt
    python scripts/evaluate.py --weights runs/crack_detect/weights/best.pt --split test
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_config
from core.evaluator import ModelEvaluator
from utils.logger import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a trained crack detection model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--weights", type=str, required=True, help="Path to model weights (.pt)")
    parser.add_argument("--split", type=str, default="test", choices=["val", "test"], help="Dataset split")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file")
    parser.add_argument("--output", type=str, default=None, help="Path to save evaluation JSON report")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    logger = get_logger("evaluate")

    args = parse_args()
    config = get_config(args.config)

    logger.info("=" * 60)
    logger.info("CRACK DETECTION — EVALUATION")
    logger.info("=" * 60)
    logger.info("Weights : %s", args.weights)
    logger.info("Split   : %s", args.split)
    logger.info("=" * 60)

    evaluator = ModelEvaluator(weights_path=args.weights, config=config)
    result = evaluator.evaluate(split=args.split)

    logger.info("")
    logger.info("=" * 60)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 60)
    logger.info("Precision   : %.4f", result.precision)
    logger.info("Recall      : %.4f", result.recall)
    logger.info("F1 Score    : %.4f", result.f1)
    logger.info("mAP@50      : %.4f", result.map50)
    logger.info("mAP@50-95   : %.4f", result.map50_95)

    if result.per_class:
        logger.info("--- Per-Class ---")
        for name, metrics in result.per_class.items():
            logger.info("  %s: %s", name, metrics)

    if result.model_info:
        logger.info("--- Model Info ---")
        for k, v in result.model_info.items():
            if k != "gpu":
                logger.info("  %s: %s", k, v)

    # Export report
    output = args.output
    if output is None:
        run_dir = Path(args.weights).parent.parent
        output = str(run_dir / "evaluation.json")

    evaluator.export_report(output)
    logger.info("Report saved: %s", output)


if __name__ == "__main__":
    main()
