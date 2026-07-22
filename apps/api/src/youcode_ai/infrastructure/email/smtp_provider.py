import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from youcode_ai.application.ports.email_gateway import (
    EmailDeliveryResult,
    EmailGateway,
    EmailMessage,
)

logger = logging.getLogger(__name__)


class SmtpEmailGateway:
    """Provider SMTP configurable."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        timeout: int = 10,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._timeout = timeout

    def send(
        self,
        message: EmailMessage,
    ) -> EmailDeliveryResult:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["To"] = message.recipient

        from_header = (
            f"{message.from_name} <{message.from_address}>"
            if message.from_name
            else message.from_address
        )
        msg["From"] = from_header

        if message.reply_to:
            msg["Reply-To"] = message.reply_to

        for key, value in message.headers.items():
            msg[key] = value

        if message.body_text:
            msg.attach(
                MIMEText(
                    message.body_text,
                    "plain",
                    "utf-8",
                )
            )

        if message.body_html:
            msg.attach(
                MIMEText(
                    message.body_html,
                    "html",
                    "utf-8",
                )
            )

        try:
            with smtplib.SMTP(
                self._host,
                self._port,
                timeout=self._timeout,
            ) as smtp:
                if self._use_tls:
                    smtp.starttls()

                if self._username:
                    smtp.login(
                        self._username,
                        self._password,
                    )

                smtp.send_message(msg)

            logger.info(
                "[EMAIL-SMTP] Sent to=%s "
                "subject='%s'",
                message.recipient,
                message.subject,
            )

            return EmailDeliveryResult(
                success=True,
                provider_message_id=(
                    msg["Message-ID"]
                ),
            )

        except smtplib.SMTPException as exc:
            logger.error(
                "[EMAIL-SMTP] Failed to=%s "
                "error_type=%s",
                message.recipient,
                type(exc).__name__,
            )

            return EmailDeliveryResult(
                success=False,
                error_message=str(exc),
            )

        except OSError as exc:
            logger.error(
                "[EMAIL-SMTP] Connection "
                "error: %s",
                type(exc).__name__,
            )

            return EmailDeliveryResult(
                success=False,
                error_message=(
                    f"Connection error: {exc}"
                ),
            )
