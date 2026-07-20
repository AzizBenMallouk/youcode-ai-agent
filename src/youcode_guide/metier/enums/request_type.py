from enum import Enum

class RequestType(str, Enum):
    WAITLIST = "waitlist"
    ACCESS_PROBLEM = "access_problem"
    TEST_RESCHEDULE = "test_reschedule"

