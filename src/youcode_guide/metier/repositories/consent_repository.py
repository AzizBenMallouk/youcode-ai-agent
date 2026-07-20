from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from youcode_guide.database.sqlite.schema.consent_grant_table import (
    ConsentGrantTable,
)


class ConsentRepository:
    def __init__(
        self,
        session_factory: Callable[
            [],
            Session,
        ],
    ) -> None:
        self.session_factory = session_factory

    def create(
        self,
        consent: ConsentGrantTable,
    ) -> ConsentGrantTable:
        with self.session_factory() as session:
            session.add(consent)
            session.commit()
            session.refresh(consent)

            return consent

    def find_by_token_hash(
        self,
        token_hash: str,
    ) -> ConsentGrantTable | None:
        with self.session_factory() as session:
            statement = select(
                ConsentGrantTable
            ).where(
                ConsentGrantTable.token_hash
                == token_hash
            )

            return session.scalar(statement)

    def mark_as_used(
        self,
        consent_id: str,
        used_at: datetime,
    ) -> None:
        with self.session_factory() as session:
            consent = session.get(
                ConsentGrantTable,
                consent_id,
            )

            if consent is None:
                raise ValueError(
                    "Consent not found."
                )

            consent.used_at = used_at

            session.commit()

    def revoke(
        self,
        consent_id: str,
        revoked_at: datetime,
    ) -> None:
        with self.session_factory() as session:
            consent = session.get(
                ConsentGrantTable,
                consent_id,
            )

            if consent is None:
                raise ValueError(
                    "Consent not found."
                )

            consent.revoked_at = revoked_at

            session.commit()