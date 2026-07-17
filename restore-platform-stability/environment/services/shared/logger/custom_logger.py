import logging
import sys
import json
from datetime import datetime, timezone
from shared.logger.context import get_correlation_id, get_request_id


class JSONLogFormatter(logging.Formatter):
    """Structured JSON formatter for production logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }

        # Inject contextual identifiers if available
        correlation_id = get_correlation_id()
        if correlation_id:
            log_obj["correlation_id"] = correlation_id

        request_id = get_request_id()
        if request_id:
            log_obj["request_id"] = request_id

        # Add any extra arguments passed to the logger
        if hasattr(record, "extra_info"):
            log_obj.update(record.extra_info)

        # Include exception traceback if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a structured logger for the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONLogFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger
