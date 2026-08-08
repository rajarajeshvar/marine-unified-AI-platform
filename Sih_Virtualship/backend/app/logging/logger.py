import json
import logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "file": record.filename,
            "line": record.lineno,
        }
        # Capture and merge any extra properties passed via extra={...}
        if hasattr(record, "extra_context"):
            log_data["context"] = record.extra_context
            
        return json.dumps(log_data)

def setup_logging():
    """Replaces standard handlers with custom JSON stdout formatting."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    # Purge standard handlers to prevent duplication
    for existing_handler in root_logger.handlers[:]:
        root_logger.removeHandler(existing_handler)
        
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Restrict excessive debug printout noise from server frameworks
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
