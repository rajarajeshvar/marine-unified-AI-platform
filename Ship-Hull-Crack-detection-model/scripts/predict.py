"""
CLI entry point for single-image inference.

Usage:
    python scripts/predict.py --image path/to/image.jpg
    python scripts/predict.py --image path/to/image.jpg --weights runs/crack_detect/weights/best.pt
    python scripts/predict.py --image path/to/image.jpg --save output.jpg
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_config
from core.predictor import CrackPredictor
from utils.logger import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run crack detection on a single image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--image", type=str, required=True, help="Path to input image")
    parser.add_argument("--weights", type=str, default=None, help="Path to model weights (.pt)")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config file")
    parser.add_argument("--confidence", type=float, default=None, help="Confidence threshold")
    parser.add_argument("--save", type=str, default=None, help="Save annotated image to this path")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    logger = get_logger("predict")

    args = parse_args()
    config = get_config(args.config)

    if args.confidence is not None:
        config.inference.confidence_threshold = args.confidence

    logger.info("=" * 60)
    logger.info("CRACK DETECTION — INFERENCE")
    logger.info("=" * 60)
    logger.info("Image   : %s", args.image)
    logger.info("Weights : %s", args.weights or config.inference.weights)
    logger.info("=" * 60)

    predictor = CrackPredictor(config)
    if args.weights:
        predictor.setup(weights_path=args.weights)

    result = predictor.predict(args.image)

    if result.error:
        logger.error("Prediction failed: %s", result.error)
        sys.exit(1)

    logger.info("")
    logger.info("RESULTS")
    logger.info("-" * 40)
    logger.info("Detections    : %d", result.num_detections)
    logger.info("Inference time: %.1f ms", result.inference_time_ms)
    logger.info("Image size    : %d x %d", result.image_width, result.image_height)
    logger.info("Model         : %s", result.model_variant)

    for i, det in enumerate(result.detections):
        logger.info(
            "  [%d] %s  conf=%.3f  bbox=%s",
            i + 1, det.class_name, det.confidence,
            [round(v, 1) for v in det.bbox_xyxy],
        )

    # Save annotated image
    if args.save and result.annotated_image_base64:
        out_path = Path(args.save)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img_bytes = base64.b64decode(result.annotated_image_base64)
        out_path.write_bytes(img_bytes)
        logger.info("Annotated image saved: %s", out_path)


if __name__ == "__main__":
    main()
