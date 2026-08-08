# Ship Hull Crack Detection

Automated structural crack detection from underwater ROV images using YOLOv8. Detects cracks in ship hull images and returns bounding boxes with confidence scores.

Part of a Smart India Hackathon project. This module handles only the computer vision pipeline.

## What it does

- Trains YOLOv8 on annotated underwater crack images
- Runs inference on new images and returns crack locations
- Exposes predictions through a REST API
- Provides a minimal web interface for uploading images and viewing results

## Dataset

- 12,012 annotated underwater hull images (YOLOv8 format)
- 1 class: `crack`
- Pre-split: 11,460 train / 368 validation / 184 test
- Resolution: 640×640
- Source: Roboflow (CC BY 4.0)

## Folder Structure

```
marine_classification/
├── dataset/                → Symlink to raw dataset
├── config/
│   ├── settings.py         Settings management (YAML + env vars)
│   └── default.yaml        Default hyperparameters and paths
├── core/
│   ├── trainer.py          Training pipeline
│   ├── evaluator.py        Evaluation and metrics
│   ├── predictor.py        Inference engine
│   └── model_manager.py    Model loading and switching
├── backend/
│   ├── app.py              FastAPI application
│   ├── schemas.py          Request/response models
│   └── routes/
│       ├── predict.py      POST /predict
│       ├── health.py       GET /health
│       ├── model.py        GET /model/info
│       └── metrics.py      GET /metrics
├── frontend/
│   └── index.html          Minimal upload + results UI
├── scripts/
│   ├── train.py            CLI: train the model
│   ├── evaluate.py         CLI: evaluate a trained model
│   └── predict.py          CLI: run inference on a single image
├── utils/
│   ├── logger.py           Logging setup
│   ├── device.py           GPU/CPU detection
│   └── image.py            Image I/O helpers
├── runs/                   Training outputs (auto-created)
├── requirements.txt
└── README.md
```

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/Mac

# Install dependencies (automatically installs CUDA 12.1 GPU PyTorch)
pip install -r requirements.txt
```

`requirements.txt` includes `--extra-index-url https://download.pytorch.org/whl/cu121`, so `pip` will automatically download and configure **PyTorch with CUDA GPU acceleration** for any NVIDIA GPU present on the machine. If no GPU is available, the system will automatically fall back to CPU without breaking.

## Training

```bash
# Default training (50 epochs, yolov8n, batch 16)
python scripts/train.py

# Custom training
python scripts/train.py --epochs 100 --model yolov8s --batch-size 32 --lr 0.001

# Resume interrupted training
python scripts/train.py --resume
```

Trained weights are saved to `runs/crack_detect/weights/best.pt` and `last.pt`.

### Configuration

Edit `config/default.yaml` to change defaults, or pass CLI arguments. Environment variables also work:

```bash
set CRACK_DETECT_TRAINING_EPOCHS=100
set CRACK_DETECT_MODEL_VARIANT=yolov8s
```

## Evaluation

```bash
python scripts/evaluate.py --weights runs/crack_detect/weights/best.pt
python scripts/evaluate.py --weights runs/crack_detect/weights/best.pt --split val
```

Outputs: Precision, Recall, mAP@50, mAP@50-95, F1 score. Saves a JSON report to the run directory.

## Inference (CLI)

```bash
python scripts/predict.py --image path/to/image.jpg
python scripts/predict.py --image path/to/image.jpg --save output.jpg --confidence 0.3
```

## API Server

```bash
# Start the server
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Open the web UI
# http://localhost:8000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Upload an image, get crack detections |
| GET | `/health` | System status, GPU info, model state |
| GET | `/model/info` | Model variant, parameters, size |
| GET | `/metrics` | Evaluation results (after running evaluate.py) |

### POST /predict

```bash
curl -X POST http://localhost:8000/predict -F "file=@image.jpg"
```

Response:
```json
{
  "num_detections": 3,
  "detections": [
    {
      "class_id": 0,
      "class_name": "crack",
      "confidence": 0.87,
      "bbox_xyxy": [120.5, 200.3, 340.1, 280.7],
      "bbox_xywhn": [0.36, 0.375, 0.343, 0.126]
    }
  ],
  "annotated_image_base64": "...",
  "inference_time_ms": 12.4,
  "model_variant": "yolov8n"
}
```

## Switching Models

Change the model variant without modifying code:

```bash
# Via CLI
python scripts/train.py --model yolov8s

# Via config
# Edit config/default.yaml → model.variant: "yolov8m"

# Via environment variable
set CRACK_DETECT_MODEL_VARIANT=yolov8l
```

Supported variants: `yolov8n`, `yolov8s`, `yolov8m`, `yolov8l`, `yolov8x`

## Future Scope

The architecture supports adding these without restructuring:

- **Multi-class detection**: corrosion, rust, paint damage, biofouling
- **YOLO segmentation**: instance segmentation for precise crack outlines
- **Video inference**: frame-by-frame detection on ROV footage
- **Live ROV stream**: real-time detection via RTSP/WebSocket
- **ONNX/TensorRT export**: optimized inference for edge deployment
- **Docker deployment**: containerized production setup
