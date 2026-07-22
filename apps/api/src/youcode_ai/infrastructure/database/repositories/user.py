from sqlalchemy import select, func
from youcode_ai.infrastructure.database.repositories.base import BaseRepository
from youcode_ai.infrastructure.database.tables.user import UserTable
from youcode_ai.domain.enums.auth import UserRole

class UserRepository(BaseRepository[UserTable]):
    def __init__(self, *, session):
        super().__init__(session=session, model_type=UserTable)

    def find_by_email(self, email: str) -> UserTable | None:
        stmt = select(UserTable).where(UserTable.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_filtered(
        self, *, page: int, page_size: int, role: str | None = None, is_active: bool | None = None
    ) -> tuple[list[UserTable], int]:
        stmt = select(UserTable)
        count_stmt = select(func.count(UserTable.id))

        if role:
            stmt = stmt.where(UserTable.role == role)
            count_stmt = count_stmt.where(UserTable.role == role)
            
        if is_active is not None:
            stmt = stmt.where(UserTable.is_active == is_active)
            count_stmt = count_stmt.where(UserTable.is_active == is_active)

        total = self.session.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(UserTable.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        items = self.session.execute(stmt).scalars().all()
        return list(items), total
