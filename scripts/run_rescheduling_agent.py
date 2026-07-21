from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
from hashlib import sha256
from uuid import uuid4

from sqlalchemy import select

from youcode_guide.agents.rescheduling.service import (
    ReschedulingAgentService,
)
from youcode_guide.database.sqlite.connection import (
    create_database_session,
)
from youcode_guide.database.sqlite.schema.consent_grant_table import (
    ConsentGrantTable,
)
from youcode_guide.database.sqlite.schema.visitor_request_table import (
    VisitorRequestTable,
)
import logging
from youcode_guide.config import settings

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)
print(
    "Test Session API:",
    settings.test_session_api_url,
)

def create_test_request() -> str:
    session = create_database_session()

    consent_id = str(uuid4())
    request_id = str(uuid4())

    unique_suffix = uuid4().hex[:8].upper()

    consent_reference = (
        f"CONS-TEST-{unique_suffix}"
    )

    request_reference = (
        f"VR-TEST-{unique_suffix}"
    )

    session_id = (
        f"test-session-{unique_suffix}"
    )

    email = "candidat.test@example.com"

    now = datetime.now(timezone.utc)

    raw_token = uuid4().hex

    token_hash = sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    subject_hash = sha256(
        email.encode("utf-8")
    ).hexdigest()

    try:
        consent = ConsentGrantTable(
            id=consent_id,
            reference=consent_reference,
            token_hash=token_hash,
            session_id=session_id,
            purpose="test_reschedule",
            subject_hash=subject_hash,
            consent_version="v1",
            created_at=now,
            expires_at=(
                now + timedelta(days=365)
            ),
            used_at=now,
            revoked_at=None,
        )

        visitor_request = (
            VisitorRequestTable(
                id=request_id,
                reference=request_reference,
                request_type=(
                    "test_reschedule"
                ),
                status="pending",
                email=email,
                language="fr",
                campus="Safi",
                platform="candidature",
                description=(
                    "Le candidat ne sera pas "
                    "disponible à la date "
                    "initialement programmée."
                ),
                scheduled_test_date=date(
                    2026,
                    8,
                    2,
                ),
                requested_test_date=date(
                    2026,
                    8,
                    10,
                ),
                consent_id=consent_id,
                created_at=now,
                updated_at=now,
            )
        )

        session.add(consent)
        session.add(visitor_request)

        session.commit()

        print(
            "Demande de test créée :"
        )
        print(
            f"- référence : "
            f"{request_reference}"
        )
        print(
            f"- consentement : "
            f"{consent_reference}"
        )
        print("- campus : Safi")
        print(
            "- test actuel : 2026-08-02"
        )
        print(
            "- date souhaitée : 2026-08-10"
        )
        print()

        return request_reference

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def display_request(
    reference: str,
) -> None:
    session = create_database_session()

    try:
        statement = select(
            VisitorRequestTable
        ).where(
            VisitorRequestTable.reference
            == reference
        )

        request = session.scalar(statement)

        if request is None:
            print(
                "Demande introuvable "
                "après traitement."
            )
            return

        print()
        print("État final de la demande :")
        print(
            f"- référence : "
            f"{request.reference}"
        )
        print(
            f"- statut : {request.status}"
        )
        print(
            f"- campus : {request.campus}"
        )

        external_session_id = getattr(
            request,
            "external_session_id",
            None,
        )

        proposed_test_date = getattr(
            request,
            "proposed_test_date",
            None,
        )

        decision_reason = getattr(
            request,
            "decision_reason",
            None,
        )

        print(
            f"- session externe : "
            f"{external_session_id}"
        )
        print(
            f"- date proposée : "
            f"{proposed_test_date}"
        )
        print(
            f"- justification : "
            f"{decision_reason}"
        )

    finally:
        session.close()


def main() -> None:
    print("YouCode Rescheduling Agent")
    print("=" * 40)
    print()

    try:
        reference = create_test_request()

        agent_service = (
            ReschedulingAgentService()
        )

        agent_session_id = str(
            uuid4()
        )

        print(
            "Lancement du "
            "Rescheduling Agent..."
        )
        print()

        response = agent_service.invoke(
            reference=reference,
            session_id=agent_session_id,
        )

        print("Réponse de l’agent :")
        print(
            response.model_dump_json(
                indent=2,
            )
        )

        display_request(reference)

    except Exception as error:
        print()
        print(
            "Le test a échoué :"
        )
        print(
            f"{type(error).__name__}: "
            f"{error}"
        )


if __name__ == "__main__":
    main()