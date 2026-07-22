from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum as SqlEnum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from datetime import datetime
from youcode_ai.infrastructure.database.base import Base
from youcode_ai.infrastructure.database.tables.common import (
    generate_uuid,
    utc_now,
    enum_values,
)
from youcode_ai.domain.enums.auth import UserRole

class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(
            UserRole,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=UserRole.ADMIN,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    refresh_tokens: Mapped[list["RefreshTokenTable"]] = relationship(
        "RefreshTokenTable",
        back_populates="user",
        cascade="all, delete-orphan",
    )
