import json
from typing import Any


def tool_response(
    payload: dict[str, Any],
) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
    )