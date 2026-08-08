"""
Pydantic schemas for API request/response models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DetectionSchema(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: List[float]
    bbox_xywhn: List[float]


class PredictionResponse(BaseModel):
    num_detections: int
    detections: List[DetectionSchema]
    annotated_image_base64: Optional[str] = None
    inference_time_ms: float
    image_size: Dict[str, int]
    model_variant: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    gpu_name: str
    device: str


class ModelInfoResponse(BaseModel):
    variant: str
    weights: Optional[str]
    device: str
    loaded: bool
    class_names: List[str]
    num_classes: int
    model_size_mb: Optional[float] = None
    total_parameters: Optional[int] = None
    total_parameters_millions: Optional[float] = None
    gpu: Dict[str, str]


class MetricsResponse(BaseModel):
    precision: float
    recall: float
    map50: float
    map50_95: float
    f1_score: float
    per_class: Dict[str, Any]
    model_info: Dict[str, Any]
    training_curves: Optional[Dict[str, List[float]]] = None
