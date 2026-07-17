from typing import Any, Dict


def format_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Common helper to format standardized API responses."""
    return {"status": "success", "message": message, "data": data}


def format_error(message: str) -> Dict[str, Any]:
    """Common helper to format standardized error responses."""
    return {"status": "error", "message": message, "data": None}
