from sqlalchemy import func, select
from sqlalchemy.orm import Session
from shared.domain.enums.campaign import CampaignStatus
from shared.infrastructure.database.repositories.base import BaseRepository
from shared.infrastructure.database.tables import NewsletterCampaignTable


class NewsletterCampaignRepository(BaseRepository[NewsletterCampaignTable]):
    def __init__(self, *, session: Session) -> None:
        super().__init__(session=session, model_type=NewsletterCampaignTable)

    def find_by_reference(self, reference: str) -> NewsletterCampaignTable | None:
        statement = select(NewsletterCampaignTable).where(
            NewsletterCampaignTable.reference == reference
        )
        return self.session.scalar(statement)

    def list_filtered(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: CampaignStatus | None = None,
    ) -> tuple[list[NewsletterCampaignTable], int]:
        statement = select(NewsletterCampaignTable)
        count_statement = select(func.count()).select_from(NewsletterCampaignTable)

        if status:
            statement = statement.where(NewsletterCampaignTable.status == status)
            count_statement = count_statement.where(
                NewsletterCampaignTable.status == status
            )

        statement = statement.order_by(NewsletterCampaignTable.created_at.desc())

        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

        items = list(self.session.scalars(statement).all())
        total = self.session.scalar(count_statement) or 0

        return items, total
