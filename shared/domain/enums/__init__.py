from shared.domain.enums.auth import (
    UserRole,
)
from shared.domain.enums.campaign import (
    CampaignStatus,
)
from shared.domain.enums.common import (
    ConsentPurpose,
    Language,
)
from shared.domain.enums.knowledge_gap import (
    KnowledgeAnswerStatus,
    KnowledgeCategory,
    KnowledgeGapStatus,
)
from shared.domain.enums.newsletter import (
    EmailDeliveryStatus,
    EmailType,
    NewsletterTopic,
    SubscriptionStatus,
)
from shared.domain.enums.request import (
    RequestStatus,
    RequestType,
)

__all__ = [
    "CampaignStatus",
    "ConsentPurpose",
    "EmailDeliveryStatus",
    "EmailType",
    "KnowledgeAnswerStatus",
    "KnowledgeCategory",
    "KnowledgeGapStatus",
    "Language",
    "NewsletterTopic",
    "RequestStatus",
    "RequestType",
    "SubscriptionStatus",
    "UserRole",
]
