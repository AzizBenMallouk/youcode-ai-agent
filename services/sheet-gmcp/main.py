import os
import json
import logging
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import gspread
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("sheet_gmcp")

def get_client() -> gspread.Client:
    """Gets an authenticated gspread client."""
    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/credentials.json")
    if os.path.exists(creds_file):
        return gspread.service_account(filename=creds_file)
    
    # Fallback to env var containing raw JSON string
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        return gspread.service_account_from_dict(creds_dict)
    
    raise ValueError("Google Sheets credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS_JSON.")

def get_sheet(spreadsheet_id: str, worksheet_name: str) -> gspread.worksheet.Worksheet:
    client = get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)


@mcp.tool(
    name="append_visitor_request",
    annotations={
        "title": "Append Visitor Request to Google Sheet",
        "description": "Saves a visitor support request into Google Sheets instead of Postgres.",
    },
)
def append_visitor_request(
    user_id: str,
    first_name: str,
    last_name: str,
    email: str,
    cin: str,
    campus: str,
    intent: str,
    details: str
) -> str:
    """Appends a new visitor request to the 'VisitorRequests' sheet."""
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not spreadsheet_id:
        return "Error: GOOGLE_SHEET_ID environment variable not set."

    try:
        sheet = get_sheet(spreadsheet_id, "VisitorRequests")
        row = [user_id, first_name, last_name, email, cin, campus, intent, details]
        sheet.append_row(row)
        return f"Successfully saved visitor request for {email}."
    except Exception as e:
        logger.error(f"Error appending visitor request: {e}")
        return f"Failed to save visitor request: {str(e)}"

@mcp.tool(
    name="append_newsletter_subscription",
    annotations={
        "title": "Append Newsletter Subscription to Google Sheet",
        "description": "Saves a newsletter subscription into Google Sheets.",
    },
)
def append_newsletter_subscription(
    email: str,
    status: str
) -> str:
    """Appends a new newsletter subscription to the 'Newsletter' sheet."""
    spreadsheet_id = os.getenv("SHEETS_DOCUMENT_ID")
    if not spreadsheet_id:
        return "Error: SHEETS_DOCUMENT_ID environment variable not set."

    try:
        sheet = get_sheet(spreadsheet_id, "Newsletter")
        row = [email, status]
        sheet.append_row(row)
        return f"Successfully saved newsletter preference for {email}."
    except Exception as e:
        logger.error(f"Error appending newsletter subscription: {e}")
        return f"Failed to save newsletter preference: {str(e)}"


# FastAPI wrapper for Docker healthcheck and mounting Streamable HTTP
app = FastAPI(title="YouCode AI — Sheet GMCP Server")
app.mount("/mcp", mcp.streamable_http_app())

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "sheet-gmcp"}
