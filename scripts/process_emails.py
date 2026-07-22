"""Worker de traitement des e-mails en attente (outbox)."""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s [%(levelname)s] "
        "%(name)s — %(message)s"
    ),
)

logger = logging.getLogger(__name__)


def main() -> None:
    from youcode_ai.infrastructure.database import (
        database_session,
    )
    from youcode_ai.infrastructure.email import (
        create_email_gateway,
    )
    from youcode_ai.core.config import settings
    from youcode_ai.application.services.email import (
        EmailService,
    )

    gateway = create_email_gateway(settings)

    with database_session() as session:
        service = EmailService(
            session=session,
            gateway=gateway,
        )

        sent_ids = service.process_pending(
            batch_size=20
        )

        if sent_ids:
            logger.info(
                "Traité %d e-mail(s).",
                len(sent_ids),
            )
        else:
            logger.info(
                "Aucun e-mail en attente."
            )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception(
            "Erreur lors du traitement "
            "des e-mails."
        )
        sys.exit(1)
