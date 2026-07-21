from enum import Enum


class NewsletterTopic(str, Enum):
    FULL_PROGRAM_REGISTRATION = (
        "full_program_registration"
    )
    BOOTCAMPS = "bootcamps"
    EVENTS = "events"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BLOCKED = "blocked"


class EmailDeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailType(str, Enum):
    SUBSCRIPTION_CONFIRMATION = (
        "subscription_confirmation"
    )
    NEWSLETTER = "newsletter"
    UNSUBSCRIBE_CONFIRMATION = (
        "unsubscribe_confirmation"
    )