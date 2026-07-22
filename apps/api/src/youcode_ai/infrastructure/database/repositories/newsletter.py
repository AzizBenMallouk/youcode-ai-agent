from sqlalchemy import select
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