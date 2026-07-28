from shared.infrastructure.database.tables.consent import (
    ConsentGrantTable,
)
from shared.infrastructure.database.tables.email_delivery import (
    EmailDeliveryTable,
)
from shared.infrastructure.database.tables.knowledge_gap import (
    KnowledgeGapTable,
)
from shared.infrastructure.database.tables.knowledge_gap_answer import (
    KnowledgeGapAnswerTable,
)
from shared.infrastructure.database.tables.knowledge_gap_question import (
    KnowledgeGapQuestionTable,
)
from shared.infrastructure.database.tables.newsletter_campaign import (
    NewsletterCampaignTable,
)
from shared.infrastructure.database.tables.newsletter_preference import (
    NewsletterPreferenceTable,
)
from shared.infrastructure.database.tables.newsletter_subscription import (
    NewsletterSubscriptionTable,
)
from shared.infrastructure.database.tables.refresh_token import (
    RefreshTokenTable,
)
from shared.infrastructure.database.tables.user import (
    UserTable,
)
from shared.infrastructure.database.tables.visitor_request import (
    VisitorRequestTable,
)

__all__ = [
    "ConsentGrantTable",
    "EmailDeliveryTable",
    "KnowledgeGapAnswerTable",
    "KnowledgeGapQuestionTable",
    "KnowledgeGapTable",
    "NewsletterCampaignTable",
    "NewsletterPreferenceTable",
    "NewsletterSubscriptionTable",
    "VisitorRequestTable",
    "UserTable",
    "RefreshTokenTable",
]
