from enum import Enum


class RequestType(str, Enum):
    TEST_RESCHEDULE = "test_reschedule"
    PLATFORM_ACCESS = "platform_access"
    LOGIN_PROBLEM = "login_problem"
    APPLICATION_PROBLEM = (
        "application_problem"
    )
    OTHER_SUPPORT = "other_support"


class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"

    AWAITING_CANDIDATE_CONFIRMATION = (
        "awaiting_candidate_confirmation"
    )

    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"