"""Email MCP Server — Generic email sending via FastMCP.

Single tool: send_email(recipient, subject, body_html, body_text?)
The agent LLM composes the full content; the MCP just delivers it.
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import FastAPI
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# ---------------------------------------------------------------------------
# Configuration (SMTP or Console fallback)
# ---------------------------------------------------------------------------
EMAIL_FROM: str = os.getenv("EMAIL_FROM_ADDRESS", "no-reply@youcode.ma")
EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "YouCode AI")
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASS: str = os.getenv("SMTP_PASS", "")
SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP("email_mcp")


def _deliver(recipient: str, subject: str, body_html: str, body_text: str) -> None:
    """Send via SMTP if configured, otherwise log to console (dev mode)."""
    if not SMTP_HOST:
        logger.info(
            "[EMAIL-CONSOLE] To=%s | Subject='%s' | Body preview: %s",
            recipient,
            subject,
            body_text[:120] or body_html[:120],
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
    msg["To"] = recipient

    if body_text:
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(EMAIL_FROM, recipient, msg.as_string())

    logger.info("Email sent to %s — Subject: %s", recipient, subject)


@mcp.tool(
    name="send_email",
    annotations={
        "title": "Send Email",
        "description": (
            "Send an email to any recipient. "
            "You provide the full recipient address, subject line, and body. "
            "Use this for rescheduling confirmations, admin alerts, or any "
            "notification that requires an email."
        ),
    },
)
def send_email(
    recipient: str,
    subject: str,
    body_html: str,
    body_text: str = "",
) -> str:
    """
    Send an email with arbitrary content.

    Args:
        recipient:  Destination email address (e.g. 'student@example.com').
        subject:    Email subject line.
        body_html:  Full HTML body. Use proper HTML formatting.
        body_text:  Plain-text fallback (optional but recommended).

    Returns:
        Confirmation string on success, error message on failure.
    """
    try:
        _deliver(recipient, subject, body_html, body_text)
        return f"Email envoyé avec succès à {recipient} — Sujet : {subject}"
    except Exception as exc:
        logger.exception("Failed to send email to %s", recipient)
        return f"Erreur lors de l'envoi de l'email à {recipient} : {exc}"


# ---------------------------------------------------------------------------
# FastAPI wrapper
# ---------------------------------------------------------------------------
mcp_app = mcp.http_app(path="/")
app = FastAPI(title="YouCode AI — Email MCP Server", lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": "email-mcp",
        "smtp_configured": bool(SMTP_HOST),
    }
