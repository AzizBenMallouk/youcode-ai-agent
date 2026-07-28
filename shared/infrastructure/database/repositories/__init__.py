from shared.infrastructure.database.repositories.base import (
    BaseRepository,
)
from shared.infrastructure.database.repositories.consent import (
    ConsentRepository,
)
from shared.infrastructure.database.repositories.email_delivery import (
    EmailDeliveryRepository,
)
from shared.infrastructure.database.repositories.knowledge_gap import (
    KnowledgeGapRepository,
)
from shared.infrastructure.database.repositories.newsletter import (
    NewsletterRepository,
)
from shared.infrastructure.database.repositories.newsletter_campaign import (
    NewsletterCampaignRepository,
)
from shared.infrastructure.database.repositories.refresh_token import (
    RefreshTokenRepository,
)
from shared.infrastructure.database.repositories.user import (
    UserRepository,
)
from shared.infrastructure.database.repositories.visitor_request import (
    VisitorRequestRepository,
)

__all__ = [
    "BaseRepository",
    "ConsentRepository",
    "EmailDeliveryRepository",
    "KnowledgeGapRepository",
    "NewsletterCampaignRepository",
    "NewsletterRepository",
    "VisitorRequestRepository",
    "UserRepository",
    "RefreshTokenRepository",
]
