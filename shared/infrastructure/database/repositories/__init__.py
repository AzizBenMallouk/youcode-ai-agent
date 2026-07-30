from shared.infrastructure.database.repositories.base import (
    BaseRepository,
)
from shared.infrastructure.database.repositories.consent import (
    ConsentRepository,
)
from shared.infrastructure.database.repositories.newsletter import (
    NewsletterRepository,
)
from shared.infrastructure.database.repositories.visitor_request import (
    VisitorRequestRepository,
)

__all__ = [
    "BaseRepository",
    "ConsentRepository",
    "NewsletterRepository",
    "VisitorRequestRepository",
]
