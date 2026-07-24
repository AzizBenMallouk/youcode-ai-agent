import json
import logging
import os
from typing import Any

import gspread
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Crée le serveur FastMCP
mcp = FastMCP("GoogleSheetsMCP")

# Identifiants
CREDENTIALS_FILE = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/home/bucketlister/Desktop/iayyyyy/youcode-ai-agent/youcode-383711-be6f512e7af2.json",
)


def get_client() -> gspread.Client:
    """Retourne un client gspread authentifié."""
    return gspread.service_account(filename=CREDENTIALS_FILE)


def ensure_sheet_exists(
    client: gspread.Client, spreadsheet_id: str, sheet_name: str, headers: list[str]
):
    """Vérifie si un onglet (worksheet) existe, sinon le crée avec les en-têtes."""
    doc = client.open_by_key(spreadsheet_id)
    try:
        worksheet = doc.worksheet(sheet_name)
        # Vérifie si la première ligne est vide, si oui, ajoute les en-têtes
        if not worksheet.row_values(1):
            worksheet.append_row(headers)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = doc.add_worksheet(
            title=sheet_name, rows=1000, cols=max(20, len(headers))
        )
        worksheet.append_row(headers)


@mcp.tool()
def append_row(spreadsheet_id: str, sheet_name: str, row_data: dict[str, Any]) -> str:
    """
    Ajoute une nouvelle ligne dans un Google Sheet spécifié.

    Args:
        spreadsheet_id: L'ID du Google Spreadsheet (trouvable dans l'URL).
        sheet_name: Le nom de l'onglet (ex: "newsletter_subscriptions").
        row_data: Dictionnaire clé-valeur représentant la ligne à insérer.
    """
    try:
        client = get_client()
        headers = list(row_data.keys())
        values = [str(val) for val in row_data.values()]

        # S'assure que l'onglet existe et a des en-têtes
        ensure_sheet_exists(client, spreadsheet_id, sheet_name, headers)

        doc = client.open_by_key(spreadsheet_id)
        worksheet = doc.worksheet(sheet_name)

        # S'assure que les en-têtes correspondent
        existing_headers = worksheet.row_values(1)

        # Prépare la ligne dans le même ordre que les en-têtes existants
        ordered_row = []
        for header in existing_headers:
            if header in row_data:
                ordered_row.append(str(row_data[header]))
            else:
                ordered_row.append("")

        # Ajoute les nouvelles colonnes si nécessaire
        for k, v in row_data.items():
            if k not in existing_headers:
                existing_headers.append(k)
                ordered_row.append(str(v))
                # Met à jour la ligne d'en-tête (une liste de liste pour update)
                worksheet.update([existing_headers], "A1")

        worksheet.append_row(ordered_row)
        return f"Successfully appended row to {sheet_name}"

    except Exception as e:
        logger.error(f"Error appending row to Google Sheets: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
def read_sheet(spreadsheet_id: str, sheet_name: str) -> str:
    """
    Lit toutes les lignes d'un Google Sheet et les retourne sous forme de JSON.
    """
    try:
        client = get_client()
        doc = client.open_by_key(spreadsheet_id)
        worksheet = doc.worksheet(sheet_name)
        records = worksheet.get_all_records()
        return json.dumps(records)
    except gspread.exceptions.WorksheetNotFound:
        return json.dumps([])
    except Exception as e:
        logger.error(f"Error reading Google Sheets: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
