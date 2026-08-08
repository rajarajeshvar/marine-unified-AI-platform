"""
Configuration management for the crack detection system.

Loads settings from default.yaml with environment variable overrides.
All paths are resolved relative to the project root.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


def _project_root() -> Path:
    """Return the project root directory (parent of config/)."""
    return Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass
class DatasetConfig:
    root: str = "dataset"
    data_yaml: str = "dataset/data.yaml"

    @property
    def root_path(self) -> Path:
        return _project_root() / self.root

    @property
    def data_yaml_path(self) -> Path:
        return _project_root() / self.data_yaml


@dataclass
class ModelConfig:
    variant: str = "yolov8n"
    num_classes: int = 1
    class_names: List[str] = field(default_factory=lambda: ["crack"])
    weights: Optional[str] = None

    @property
    def weights_path(self) -> Optional[Path]:
        if self.weights is None:
            return None
        p = Path(self.weights)
        return p if p.is_absolute() else _project_root() / p


@dataclass
class TrainingConfig:
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 640
    learning_rate: float = 0.01
    optimizer: str = "auto"
    patience: int = 10
    save_period: int = 5
    resume: bool = False
    resume_weights: Optional[str] = None
    project: str = "runs"
    name: str = "crack_detect"
    device: str = "auto"

    @property
    def project_path(self) -> Path:
        return _project_root() / self.project

    @property
    def resume_weights_path(self) -> Optional[Path]:
        if self.resume_weights is None:
            return None
        p = Path(self.resume_weights)
        return p if p.is_absolute() else _project_root() / p


@dataclass
class InferenceConfig:
    weights: str = "runs/crack_detect/weights/best.pt"
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    image_size: int = 640
    device: str = "auto"

    @property
    def weights_path(self) -> Path:
        p = Path(self.weights)
        return p if p.is_absolute() else _project_root() / p


@dataclass
class AppConfig:
    """Top-level configuration aggregating all sub-configs."""

    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)

    @staticmethod
    def from_yaml(path: Optional[str] = None) -> "AppConfig":
        """
        Load configuration from a YAML file.

        Falls back to config/default.yaml if no path is provided.
        Environment variables override YAML values using the pattern:
            CRACK_DETECT_<SECTION>_<KEY>  (e.g. CRACK_DETECT_TRAINING_EPOCHS=100)
        """
        if path is None:
            yaml_path = _project_root() / "config" / "default.yaml"
        else:
            yaml_path = Path(path)
            if not yaml_path.is_absolute():
                yaml_path = _project_root() / yaml_path

        raw = _load_yaml(yaml_path) if yaml_path.exists() else {}

        config = AppConfig(
            dataset=_build_section(DatasetConfig, raw.get("dataset", {}), "DATASET"),
            model=_build_section(ModelConfig, raw.get("model", {}), "MODEL"),
            training=_build_section(TrainingConfig, raw.get("training", {}), "TRAINING"),
            inference=_build_section(InferenceConfig, raw.get("inference", {}), "INFERENCE"),
        )
        return config


def _build_section(cls, yaml_data: dict, env_prefix: str):
    """
    Build a dataclass instance from YAML data with env var overrides.

    Environment variables follow: CRACK_DETECT_<env_prefix>_<FIELD_NAME>
    """
    kwargs = {}
    for f in cls.__dataclass_fields__:
        env_key = f"CRACK_DETECT_{env_prefix}_{f.upper()}"
        env_val = os.environ.get(env_key)

        if env_val is not None:
            # Cast env value to the field's type
            field_type = cls.__dataclass_fields__[f].type
            kwargs[f] = _cast_env(env_val, field_type)
        elif f in yaml_data:
            kwargs[f] = yaml_data[f]

    return cls(**kwargs)


def _cast_env(value: str, type_hint: str):
    """Cast an environment variable string to the appropriate Python type."""
    if type_hint in ("int",):
        return int(value)
    if type_hint in ("float",):
        return float(value)
    if type_hint in ("bool",):
        return value.lower() in ("true", "1", "yes")
    return value


# Convenience: default config singleton
_default_config: Optional[AppConfig] = None


def get_config(path: Optional[str] = None) -> AppConfig:
    """Get the application config, loading it once and caching."""
    global _default_config
    if _default_config is None or path is not None:
        _default_config = AppConfig.from_yaml(path)
    return _default_config
