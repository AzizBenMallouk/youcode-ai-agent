from __future__ import annotations

import html
import logging

logger = logging.getLogger(__name__)


class EmailTemplateRenderer:
    """Moteur de templates e-mail."""

    _TEMPLATES: dict[
        str,
        tuple[
            str,  # subject
            str,  # html template
            str,  # text template
        ],
    ] = {
        "test_reschedule_confirmation": (
            "YouCode — Confirmation de report de test",
            (
                "<html><body>"
                "<h2>Confirmation de report</h2>"
                "<p>Bonjour,</p>"
                "<p>Votre demande de report de test "
                "(référence : <strong>{reference}</strong>) "
                "a été validée.</p>"
                "<p><strong>Campus :</strong> {campus}</p>"
                "<p><strong>Nouvelle date :</strong> {new_date}</p>"
                "<p><strong>Heure :</strong> {new_time}</p>"
                "<p>Veuillez vous présenter à l'heure "
                "indiquée avec une pièce d'identité.</p>"
                "<p>Cordialement,<br/>L'équipe YouCode</p>"
                "</body></html>"
            ),
            (
                "Confirmation de report\n\n"
                "Bonjour,\n\n"
                "Votre demande de report de test "
                "(référence : {reference}) a été validée.\n\n"
                "Campus : {campus}\n"
                "Nouvelle date : {new_date}\n"
                "Heure : {new_time}\n\n"
                "Veuillez vous présenter à l'heure "
                "indiquée avec une pièce d'identité.\n\n"
                "Cordialement,\nL'équipe YouCode"
            ),
        ),
        "support_acknowledgement": (
            "YouCode — Accusé de réception",
            (
                "<html><body>"
                "<h2>Demande reçue</h2>"
                "<p>Bonjour,</p>"
                "<p>Nous avons bien reçu votre demande "
                "(référence : <strong>{reference}</strong>).</p>"
                "<p>Notre équipe la traitera dans les "
                "meilleurs délais.</p>"
                "<p>Cordialement,<br/>L'équipe YouCode</p>"
                "</body></html>"
            ),
            (
                "Demande reçue\n\n"
                "Bonjour,\n\n"
                "Nous avons bien reçu votre demande "
                "(référence : {reference}).\n\n"
                "Notre équipe la traitera dans les "
                "meilleurs délais.\n\n"
                "Cordialement,\nL'équipe YouCode"
            ),
        ),
        "newsletter_confirmation": (
            "YouCode — Confirmation d'abonnement",
            (
                "<html><body>"
                "<h2>Abonnement confirmé</h2>"
                "<p>Bonjour,</p>"
                "<p>Votre abonnement à la newsletter "
                "YouCode est confirmé.</p>"
                "<p><strong>Sujets :</strong> {topics}</p>"
                "<p>Pour vous désinscrire, "
                '<a href="{unsubscribe_url}">'
                "cliquez ici</a>.</p>"
                "<p>Cordialement,<br/>L'équipe YouCode</p>"
                "</body></html>"
            ),
            (
                "Abonnement confirmé\n\n"
                "Bonjour,\n\n"
                "Votre abonnement à la newsletter "
                "YouCode est confirmé.\n\n"
                "Sujets : {topics}\n\n"
                "Pour vous désinscrire : "
                "{unsubscribe_url}\n\n"
                "Cordialement,\nL'équipe YouCode"
            ),
        ),
        "newsletter_content": (
            "{subject}",
            (
                "<html><body>"
                "{content}"
                '<p><a href="{unsubscribe_url}">'
                "Se désinscrire</a></p>"
                "</body></html>"
            ),
            (
                "{content}\n\n"
                "Se désinscrire : {unsubscribe_url}"
            ),
        ),
    }

    def render(
        self,
        template_name: str,
        payload: dict,
    ) -> tuple[str, str, str]:
        """Retourne (subject, html, text)."""

        if template_name not in self._TEMPLATES:
            logger.warning(
                "Template '%s' inconnue, "
                "utilisation du fallback.",
                template_name,
            )
            return (
                payload.get(
                    "subject", "YouCode"
                ),
                payload.get("body", ""),
                payload.get("body_text", ""),
            )

        subject_tpl, html_tpl, text_tpl = (
            self._TEMPLATES[template_name]
        )

        safe_payload = {
            k: html.escape(str(v))
            for k, v in payload.items()
        }

        return (
            subject_tpl.format_map(
                payload
            ),
            html_tpl.format_map(
                safe_payload
            ),
            text_tpl.format_map(payload),
        )
