import os
import json
import logging
from fastapi import FastAPI
from fastmcp import FastMCP
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

def get_sheet(spreadsheet_id: str, worksheet_name: str, headers: list[str] = None) -> gspread.worksheet.Worksheet:
    client = get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
        if headers:
            sheet.append_row(headers)
        return sheet


@mcp.tool(
    name="generate_admin_report",
    annotations={
        "title": "Generate Admin Report in Google Sheets",
        "description": "Creates a new sheet tab and dumps JSON data into it, returning the Google Sheet URL.",
    },
)
def generate_admin_report(
    sheet_title: str,
    data_json: str
) -> str:
    """Generates an admin report from JSON data."""
    import json
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not spreadsheet_id:
        return "Error: GOOGLE_SHEET_ID environment variable not set."

    try:
        data = json.loads(data_json)
        if not data:
            return "No data provided."
            
        headers = list(data[0].keys())
        sheet = get_sheet(spreadsheet_id, sheet_title, headers)
        
        # Clear existing data in case we are updating the same sheet
        sheet.clear()
        sheet.append_row(headers)
        
        rows = []
        for item in data:
            rows.append([str(item.get(h, "")) for h in headers])
            
        if rows:
            sheet.append_rows(rows)
            
        return f"Report generated successfully. Link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    except Exception as e:
        logger.error(f"Error generating admin report: {e}")
        return f"Failed to generate report: {str(e)}"



# FastAPI wrapper for Docker healthcheck and mounting Streamable HTTP
mcp_app = mcp.http_app(path="/")
app = FastAPI(title="YouCode AI — Sheet GMCP Server", lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "sheet-gmcp"}
