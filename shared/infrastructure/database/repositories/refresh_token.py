from datetime import datetime, timezone

from sqlalchemy import delete, select
from shared.infrastructure.database.repositories.base import BaseRepository
from shared.infrastructure.database.tables.refresh_token import RefreshTokenTable


class RefreshTokenRepository(BaseRepository[RefreshTokenTable]):
    def __init__(self, *, session):
        super().__init__(session=session, model_type=RefreshTokenTable)

    def find_by_token_hash(self, token_hash: str) -> RefreshTokenTable | None:
        stmt = select(RefreshTokenTable).where(
            RefreshTokenTable.token_hash == token_hash
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_active_for_user(self, user_id: str) -> list[RefreshTokenTable]:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshTokenTable).where(
            RefreshTokenTable.user_id == user_id,
            RefreshTokenTable.revoked_at.is_(None),
            RefreshTokenTable.expires_at > now,
        )
        return list(self.session.execute(stmt).scalars().all())

    def revoke_all_for_user(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshTokenTable).where(
            RefreshTokenTable.user_id == user_id, RefreshTokenTable.revoked_at.is_(None)
        )
        tokens = self.session.execute(stmt).scalars().all()
        for token in tokens:
            token.revoked_at = now

    def cleanup_expired(self) -> None:
        now = datetime.now(timezone.utc)
        stmt = delete(RefreshTokenTable).where(RefreshTokenTable.expires_at <= now)
        self.session.execute(stmt)
