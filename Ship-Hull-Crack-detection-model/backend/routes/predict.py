"""
Prediction endpoint: accepts image upload, returns detections.
"""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, HTTPException

from backend.schemas import PredictionResponse

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Run crack detection on an uploaded image.

    Accepts: multipart/form-data with a single image file.
    Returns: detections, annotated image (base64), inference time.
    """
    from backend.app import get_predictor

    predictor = get_predictor()
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Train a model first or check weights path.",
        )

    # Read file bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    result = predictor.predict_bytes(file_bytes, filename=file.filename)

    if result.error:
        raise HTTPException(status_code=400, detail=result.error)

    return PredictionResponse(**result.to_dict())
