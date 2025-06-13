"""
Enhanced Node Serialization Utilities
"""

import json
from datetime import datetime
from typing import Any, Dict

class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def serialize_for_json(obj: Any) -> Dict[str, Any]:
    """Serialize objects for JSON response"""
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]

    if hasattr(obj, '__dict__'):
        return {k: serialize_for_json(v) for k, v in obj.__dict__.items() 
                if not k.startswith('_')}

    return str(obj)

def safe_json_loads(data: str) -> Any:
    """Safely load JSON data"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely dump JSON data with datetime support"""
    try:
        return json.dumps(obj, cls=DateTimeJSONEncoder, **kwargs)
    except TypeError as e:
        # Fallback to serializing the object first
        return json.dumps(serialize_for_json(obj), **kwargs)