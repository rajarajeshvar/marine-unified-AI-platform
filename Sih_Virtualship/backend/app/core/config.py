import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Marine Vessel Digital Twin API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Databases
    DATABASE_URL: str
    REDIS_URL: str
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return v
    
    # WebSockets Configuration
    WS_HEARTBEAT_INTERVAL_SECONDS: int = 10
    WS_HEARTBEAT_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def thresholds(self) -> dict:
        import os
        import yaml
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "thresholds.yaml")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    @property
    def alerts_config(self) -> dict:
        import os
        import yaml
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "alerts.yaml")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    @property
    def simulator_config(self) -> dict:
        import os
        import yaml
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "simulator.yaml")
        with open(path, "r") as f:
            return yaml.safe_load(f)

settings = Settings()
