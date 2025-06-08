import json
from datetime import datetime
from typing import Any


def serialize_for_json(obj: Any) -> Any:
    """Convert datetime objects and other non-serializable objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (list, tuple)):
                result[key] = [serialize_for_json(item) for item in value]
            elif isinstance(value, dict):
                result[key] = {k: serialize_for_json(v) for k, v in value.items()}
            else:
                result[key] = value
        return result
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj


class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
