from bson import ObjectId
from typing import Any, Dict, List, Union


def convert_objectid_to_str(obj: Any) -> Any:
    """
    Convertit récursivement tous les ObjectId en strings dans un objet Python.

    Args:
        obj: L'objet à convertir (dict, list, ObjectId, etc.)

    Returns:
        L'objet avec tous les ObjectId convertis en strings
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_objectid_to_str(obj.__dict__)
    else:
        return obj