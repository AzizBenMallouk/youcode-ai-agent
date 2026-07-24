from enum import Enum


class NewsletterTopic(str, Enum):
    FULL_PROGRAM_REGISTRATION = "full_program_registration"
    BOOTCAMPS = "bootcamps"
    EVENTS = "events"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BLOCKED = "blocked"


class EmailDeliveryStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailType(str, Enum):
    SUBSCRIPTION_CONFIRMATION = "subscription_confirmation"
    NEWSLETTER = "newsletter"
    UNSUBSCRIBE_CONFIRMATION = "unsubscribe_confirmation"
    SUPPORT_ACKNOWLEDGEMENT = "support_acknowledgement"
    TEST_RESCHEDULE_CONFIRMATION = "test_reschedule_confirmation"
