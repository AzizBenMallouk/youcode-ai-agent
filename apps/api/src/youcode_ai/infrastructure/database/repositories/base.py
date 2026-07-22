from typing import (
    Generic,
    TypeVar,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_ai.infrastructure.database.base import (
    Base,
)


ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class BaseRepository(
    Generic[ModelType]
):
    def __init__(
        self,
        *,
        session: Session,
        model_type: type[ModelType],
    ) -> None:
        self.session = session
        self.model_type = model_type

    def add(
        self,
        entity: ModelType,
    ) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)

        return entity

    def get_by_id(
        self,
        entity_id: str,
    ) -> ModelType | None:
        return self.session.get(
            self.model_type,
            entity_id,
        )

    def list_all(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelType]:
        statement = (
            select(self.model_type)
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        self.session.delete(entity)
        self.session.flush()

    def save(
        self,
        entity: ModelType,
    ) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)

        return entity