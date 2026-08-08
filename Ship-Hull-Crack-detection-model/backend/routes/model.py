"""
Model information endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import ModelInfoResponse

router = APIRouter()


@router.get("/model/info", response_model=ModelInfoResponse)
async def model_info():
    """Return model metadata: variant, parameters, size, device."""
    from backend.app import get_model_manager

    manager = get_model_manager()
    if not manager.is_loaded:
        raise HTTPException(status_code=503, detail="No model loaded.")

    info = manager.get_info()
    return ModelInfoResponse(**info)
