import json


def serialize_error(
    *,
    code: str,
    message: str,
) -> str:
    return json.dumps(
        {
            "success": False,
            "error_code": code,
            "message": message,
        },
        ensure_ascii=False,
    )