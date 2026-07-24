from sqlalchemy.orm import Session
from youcode_ai.domain.enums.auth import UserRole
from youcode_ai.domain.exceptions import DuplicateEmailError
from youcode_ai.infrastructure.database.repositories.user import UserRepository
from youcode_ai.infrastructure.database.tables.user import UserTable
from youcode_ai.infrastructure.security.password import hash_password


class AdminUserService:
    def __init__(self, *, session: Session):
        self.session = session
        self.user_repo = UserRepository(session=session)

    def create_user(
        self, *, email: str, password: str, full_name: str, role: str
    ) -> UserTable:
        if self.user_repo.find_by_email(email):
            raise DuplicateEmailError("User with this email already exists")

        user = UserTable(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole(role),
            is_active=True,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_users(
        self,
        *,
        page: int,
        page_size: int,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[UserTable], int]:
        return self.user_repo.list_filtered(
            page=page, page_size=page_size, role=role, is_active=is_active
        )

    def update_user(
        self,
        *,
        user_id: str,
        full_name: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> UserTable:
        user = self.user_repo.get_by_id(user_id)
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = UserRole(role)
        if is_active is not None:
            user.is_active = is_active

        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user(self, *, user_id: str) -> UserTable:
        return self.user_repo.get_by_id(user_id)
