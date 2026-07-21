from datetime import datetime, timezone

from youcode_guide.database.sqlite.connection import (
    Base,
    engine,
)
from youcode_guide.database.sqlite.schema.consent_grant_table import ConsentGrantTable
from youcode_guide.database.sqlite.schema.registration_settings_table import RegistrationSettingsTable
from youcode_guide.database.sqlite.schema.visitor_request_table import VisitorRequestTable
from youcode_guide.database.sqlite.schema.knowledge_gap_table import KnowledgeGapTable
from youcode_guide.database.sqlite.schema.knowledge_gap_question_table import KnowledgeGapQuestionTable
from youcode_guide.database.sqlite.schema.knowledge_article_table import KnowledgeArticleTable
from youcode_guide.database.sqlite.schema.knowledge_gap_article_table import KnowledgeGapArticleTable
from youcode_guide.metier.models.update_registration_status import UpdateRegistrationStatus
from youcode_guide.metier.enums.registration_state import RegistrationState
from youcode_guide.metier.services.registration_service import (
    create_registration_service,
)


def main() -> None:
    # L'import de RegistrationSettingsTable
    # garantit que SQLAlchemy connaît la table.
    _ = ConsentGrantTable
    _ = RegistrationSettingsTable
    _ = VisitorRequestTable
    _ = KnowledgeGapTable
    _ = KnowledgeGapQuestionTable
    _ = KnowledgeArticleTable
    _ = KnowledgeGapArticleTable


    Base.metadata.create_all(engine)

    service = create_registration_service()

    current = service.get_current_status()

    if current.status == RegistrationState.UNKNOWN:
        service.update_status(
            UpdateRegistrationStatus(
                status=RegistrationState.UNKNOWN,
                message=(
                    "Le statut des inscriptions "
                    "n'a pas encore été configuré."
                ),
            )
        )

    print("Database initialized.")
    print(
        f"Date: "
        f"{datetime.now(timezone.utc).isoformat()}"
    )


if __name__ == "__main__":
    main()