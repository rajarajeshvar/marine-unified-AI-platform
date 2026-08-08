"""
FastAPI application for crack detection.

Loads the model on startup, serves prediction/health/model/metrics endpoints,
and serves the minimal frontend at /.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import AppConfig, get_config
from core.predictor import CrackPredictor
from core.model_manager import ModelManager
from utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

# Module-level singletons (initialized during lifespan)
_predictor: CrackPredictor | None = None
_model_manager: ModelManager | None = None
_config: AppConfig | None = None


def get_predictor() -> CrackPredictor:
    assert _predictor is not None, "Predictor not initialized"
    return _predictor


def get_model_manager() -> ModelManager:
    assert _model_manager is not None, "ModelManager not initialized"
    return _model_manager


def get_config_instance() -> AppConfig:
    assert _config is not None, "Config not initialized"
    return _config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, clean up on shutdown."""
    global _predictor, _model_manager, _config

    setup_logging()
    _config = get_config()

    logger.info("Starting crack detection API...")

    # Initialize predictor
    _predictor = CrackPredictor(_config)
    try:
        _predictor.setup()
        logger.info("Model loaded successfully.")
    except FileNotFoundError as e:
        logger.warning("Model weights not found: %s", e)
        logger.warning("API will start without a model. Train one first.")

    # Initialize model manager
    _model_manager = ModelManager(_config)
    try:
        _model_manager.load()
    except FileNotFoundError:
        logger.warning("ModelManager: weights not found. Endpoints will return 503.")

    yield

    logger.info("Shutting down crack detection API.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Ship Hull Crack Detection API",
        description="Detect structural cracks in underwater ship hull images using YOLOv8.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    from backend.routes.predict import router as predict_router
    from backend.routes.health import router as health_router
    from backend.routes.model import router as model_router
    from backend.routes.metrics import router as metrics_router

    app.include_router(predict_router, tags=["prediction"])
    app.include_router(health_router, tags=["health"])
    app.include_router(model_router, tags=["model"])
    app.include_router(metrics_router, tags=["metrics"])

    # Serve frontend
    frontend_dir = PROJECT_ROOT / "frontend"
    if frontend_dir.exists():
        @app.get("/", include_in_schema=False)
        async def serve_frontend():
            return FileResponse(str(frontend_dir / "index.html"))

        app.mount(
            "/static",
            StaticFiles(directory=str(frontend_dir)),
            name="static",
        )

    return app


# ASGI app instance for uvicorn
app = create_app()
