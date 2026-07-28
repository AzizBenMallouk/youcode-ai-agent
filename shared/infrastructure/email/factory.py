from shared.application.ports.email_gateway import (
    EmailGateway,
)
from shared.infrastructure.email.console_provider import (
    ConsoleEmailGateway,
)
from shared.infrastructure.email.smtp_provider import (
    SmtpEmailGateway,
)


def create_email_gateway(
    settings,
) -> EmailGateway:
    """Sélectionne le provider d'e-mail selon la configuration."""

    provider = settings.email_provider.lower()

    if provider == "smtp":
        return SmtpEmailGateway(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
            timeout=settings.smtp_timeout,
        )

    return ConsoleEmailGateway()
