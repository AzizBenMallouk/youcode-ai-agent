from typing import (
    Any,
    Generic,
    TypeVar,
)

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import (
    ColumnElement,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)

ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class BaseRepository(Generic[ModelType]):
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

    def save(
        self,
        entity: ModelType,
    ) -> ModelType:
        """
        Sauvegarde une nouvelle entité ou les
        modifications d'une entité existante.
        """

        return self.add(entity)

    def get_by_id(
        self,
        entity_id: Any,
    ) -> ModelType | None:
        return self.session.get(
            self.model_type,
            entity_id,
        )

    def find_one(
        self,
        *conditions: ColumnElement[bool],
    ) -> ModelType | None:
        statement = select(self.model_type).where(*conditions).limit(1)

        return self.session.scalar(statement)

    def count(
        self,
        *conditions: ColumnElement[bool],
    ) -> int:
        statement = select(func.count()).select_from(self.model_type).where(*conditions)

        return self.session.scalar(statement) or 0

    def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        conditions: list[ColumnElement[bool]] | None = None,
        order_by: Any | None = None,
    ) -> tuple[
        list[ModelType],
        int,
    ]:
        if page < 1:
            raise ValueError("page must be greater than 0.")

        if page_size < 1:
            raise ValueError("page_size must be greater than 0.")

        filters = conditions or []

        total = self.count(*filters)

        statement = select(self.model_type).where(*filters)

        if order_by is not None:
            statement = statement.order_by(order_by)

        statement = statement.offset((page - 1) * page_size).limit(page_size)

        entities = list(self.session.scalars(statement).all())

        return entities, total

    def list_all(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModelType]:
        statement = select(self.model_type).offset(offset).limit(limit)

        return list(self.session.scalars(statement).all())

    def delete(
        self,
        entity: ModelType,
    ) -> None:
        self.session.delete(entity)
        self.session.flush()
