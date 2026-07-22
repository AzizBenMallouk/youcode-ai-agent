from datetime import datetime, timezone

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from youcode_ai.domain.enums import (
    SubscriptionStatus,
)
from youcode_ai.infrastructure.database.repositories.base import (
    BaseRepository,
)
from youcode_ai.infrastructure.database.tables import (
    NewsletterSubscriptionTable,
    NewsletterPreferenceTable,
)


class NewsletterRepository(
    BaseRepository[
        NewsletterSubscriptionTable
    ]
):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=(
                NewsletterSubscriptionTable
            ),
        )

    def find_by_email(
        self,
        email: str,
    ) -> NewsletterSubscriptionTable | None:
        statement = (
            select(
                NewsletterSubscriptionTable
            )
            .options(
                selectinload(
                    NewsletterSubscriptionTable
                    .preferences
                )
            )
            .where(
                NewsletterSubscriptionTable
                .email
                == email.lower()
            )
        )

        return self.session.scalar(
            statement
        )

    def list_active(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[
        NewsletterSubscriptionTable
    ]:
        statement = (
            select(
                NewsletterSubscriptionTable
            )
            .options(
                selectinload(
                    NewsletterSubscriptionTable
                    .preferences
                )
            )
            .where(
                NewsletterSubscriptionTable
                .status
                == SubscriptionStatus.ACTIVE
            )
            .order_by(
                NewsletterSubscriptionTable
                .created_at
                .desc()
            )
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def activate(
        self,
        subscription: NewsletterSubscriptionTable,
        *,
        language: str,
        consent_id: str,
    ) -> NewsletterSubscriptionTable:
        now = datetime.now(timezone.utc)

        subscription.status = "active"
        subscription.language = language
        subscription.consent_id = consent_id
        subscription.subscribed_at = now
        subscription.unsubscribed_at = None
        subscription.updated_at = now

        self.session.flush()

        return subscription

    def deactivate(
        self,
        subscription: NewsletterSubscriptionTable,
    ) -> NewsletterSubscriptionTable:
        now = datetime.now(timezone.utc)

        subscription.status = "unsubscribed"
        subscription.unsubscribed_at = now
        subscription.updated_at = now

        self.session.flush()

        return subscription

    def replace_preferences(
        self,
        *,
        subscription_id: str,
        topics: list[str],
    ) -> None:
        """
        Remplace les anciennes préférences par
        la nouvelle sélection.
        """

        self.session.execute(
            delete(
                NewsletterPreferenceTable
            ).where(
                NewsletterPreferenceTable
                .subscription_id
                == subscription_id
            )
        )

        unique_topics = list(
            dict.fromkeys(topics)
        )

        now = datetime.now(timezone.utc)

        for topic in unique_topics:
            self.session.add(
                NewsletterPreferenceTable(
                    subscription_id=(
                        subscription_id
                    ),
                    topic=topic,
                    created_at=now,
                )
            )

        self.session.flush()