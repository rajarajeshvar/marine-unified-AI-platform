"""
Health check endpoint.
"""

from __future__ import annotations

import torch
from fastapi import APIRouter

from backend.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """Return system health: model status, GPU availability."""
    from backend.app import get_predictor

    predictor = get_predictor()
    gpu_available = torch.cuda.is_available()

    return HealthResponse(
        status="ok",
        model_loaded=predictor.is_loaded,
        gpu_available=gpu_available,
        gpu_name=torch.cuda.get_device_name(0) if gpu_available else "N/A",
        device=predictor.device if predictor.is_loaded else "not loaded",
    )
