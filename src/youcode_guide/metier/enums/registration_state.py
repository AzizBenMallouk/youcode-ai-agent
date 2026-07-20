from enum import Enum

class RegistrationState(str, Enum):
    UNKNOWN = "unknown"
    SCHEDULED = "scheduled"
    OPEN = "open"
    CLOSED = "closed"
