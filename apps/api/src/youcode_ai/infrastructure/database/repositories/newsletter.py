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
    NewsletterPreferenceTable,
    NewsletterSubscriptionTable,
)


class NewsletterRepository(BaseRepository[NewsletterSubscriptionTable]):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=(NewsletterSubscriptionTable),
        )

    def find_by_email(
        self,
        email: str,
    ) -> NewsletterSubscriptionTable | None:
        statement = (
            select(NewsletterSubscriptionTable)
            .options(selectinload(NewsletterSubscriptionTable.preferences))
            .where(NewsletterSubscriptionTable.email == email.lower())
        )

        return self.session.scalar(statement)

    def list_active(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NewsletterSubscriptionTable]:
        statement = (
            select(NewsletterSubscriptionTable)
            .options(selectinload(NewsletterSubscriptionTable.preferences))
            .where(NewsletterSubscriptionTable.status == SubscriptionStatus.ACTIVE)
            .order_by(NewsletterSubscriptionTable.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.session.scalars(statement).all())

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
            delete(NewsletterPreferenceTable).where(
                NewsletterPreferenceTable.subscription_id == subscription_id
            )
        )

        unique_topics = list(dict.fromkeys(topics))

        now = datetime.now(timezone.utc)

        for topic in unique_topics:
            self.session.add(
                NewsletterPreferenceTable(
                    subscription_id=(subscription_id),
                    topic=topic,
                    created_at=now,
                )
            )

        self.session.flush()

    def list_filtered(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        campus: str | None = None,
        language: str | None = None,
        topic: str | None = None,
    ) -> tuple[list[NewsletterSubscriptionTable], int]:
        from sqlalchemy import func

        statement = select(NewsletterSubscriptionTable).options(
            selectinload(NewsletterSubscriptionTable.preferences)
        )
        count_statement = select(func.count(NewsletterSubscriptionTable.id.distinct()))

        if status:
            statement = statement.where(NewsletterSubscriptionTable.status == status)
            count_statement = count_statement.where(
                NewsletterSubscriptionTable.status == status
            )

        if campus:
            statement = statement.where(NewsletterSubscriptionTable.campus == campus)
            count_statement = count_statement.where(
                NewsletterSubscriptionTable.campus == campus
            )

        if language:
            statement = statement.where(
                NewsletterSubscriptionTable.language == language
            )
            count_statement = count_statement.where(
                NewsletterSubscriptionTable.language == language
            )

        if topic:
            statement = statement.join(NewsletterSubscriptionTable.preferences).where(
                NewsletterPreferenceTable.topic == topic
            )
            count_statement = count_statement.join(
                NewsletterSubscriptionTable.preferences
            ).where(NewsletterPreferenceTable.topic == topic)

        statement = statement.order_by(NewsletterSubscriptionTable.created_at.desc())
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        items = list(self.session.scalars(statement).unique().all())
        total = self.session.scalar(count_statement) or 0

        return items, total

    def get_active_by_criteria(
        self,
        *,
        topics: list[str] | None = None,
        campuses: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> list[NewsletterSubscriptionTable]:
        statement = select(NewsletterSubscriptionTable).where(
            NewsletterSubscriptionTable.status == SubscriptionStatus.ACTIVE
        )

        if campuses:
            statement = statement.where(
                NewsletterSubscriptionTable.campus.in_(campuses)
            )

        if languages:
            statement = statement.where(
                NewsletterSubscriptionTable.language.in_(languages)
            )

        if topics:
            statement = statement.join(NewsletterSubscriptionTable.preferences).where(
                NewsletterPreferenceTable.topic.in_(topics)
            )

        return list(self.session.scalars(statement).unique().all())
