from datetime import (
    datetime,
    timezone,
)
from enum import Enum
from uuid import uuid4


def generate_uuid() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def enum_values(
    enum_class: type[Enum],
) -> list[str]:
    return [
        item.value
        for item in enum_class
    ]