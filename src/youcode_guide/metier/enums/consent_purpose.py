from enum import Enum

class ConsentPurpose(str, Enum):
    WAITLIST_NOTIFICATION = "waitlist_notification"
    ACCESS_SUPPORT = "access_support"
    TEST_RESCHEDULE = "test_reschedule"

