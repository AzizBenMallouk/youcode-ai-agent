import os
import logging
import time
from fastapi import FastAPI
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("email_mcp")

@mcp.tool(
    name="send_rescheduling_email",
    annotations={
        "title": "Send Rescheduling Email",
        "description": "Sends a mock email to a candidate with their new rescheduled test date.",
    },
)
def send_rescheduling_email(
    email: str,
    old_date: str,
    new_date: str,
    campus: str
) -> str:
    """Sends an email confirming a rescheduled admission test."""
    logger.info(f"--- EMAIL TOOL ACTIVATED VIA DEDICATED MCP ---")
    logger.info(f"Sending rescheduling email to {email}")
    logger.info(f"Campus: {campus}")
    logger.info(f"Old Date: {old_date} -> New Date: {new_date}")
    
    # Simulate network delay
    time.sleep(1)
    
    logger.info(f"Email successfully sent to {email}.")
    logger.info(f"---------------------------------------------")
    return f"Email sent successfully to {email}."

# FastAPI wrapper for Docker healthcheck and mounting Streamable HTTP
mcp_app = mcp.http_app(path="/")
app = FastAPI(title="YouCode AI — Email MCP Server", lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "email-mcp"}
