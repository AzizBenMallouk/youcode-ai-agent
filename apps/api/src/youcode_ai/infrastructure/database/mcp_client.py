import logging
import os
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPSheetsClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        """Connects to the local Python MCP server."""
        server_script = os.path.join(
            os.path.dirname(__file__), "..", "mcp", "google_sheets_server.py"
        )

        server_params = StdioServerParameters(
            command=sys.executable, args=[server_script], env=os.environ.copy()
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.read, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.read, self.write)
            )
            await self.session.initialize()
            logger.info("Successfully connected to Google Sheets MCP Server")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Server: {e}")
            raise

    async def disconnect(self):
        """Closes the MCP connection."""
        await self.exit_stack.aclose()
        self.session = None

    async def append_row(self, sheet_name: str, row_data: dict) -> str:
        """Calls the append_row tool on the MCP server."""
        if not self.session:
            raise RuntimeError("MCP Client is not connected")

        spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
        if not spreadsheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable is missing")

        result = await self.session.call_tool(
            "append_row",
            arguments={
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "row_data": row_data,
            },
        )

        try:
            return str(result.content[0].text)
        except Exception:
            return str(result.content)

    async def read_sheet(self, sheet_name: str) -> list[dict]:
        """Calls the read_sheet tool on the MCP server."""
        if not self.session:
            raise RuntimeError("MCP Client is not connected")

        spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
        if not spreadsheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable is missing")

        result = await self.session.call_tool(
            "read_sheet",
            arguments={"spreadsheet_id": spreadsheet_id, "sheet_name": sheet_name},
        )

        import json

        try:
            return json.loads(str(result.content[0].text))
        except Exception:
            return []

    def sync_append_row(self, sheet_name: str, row_data: dict) -> str:
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
        return asyncio.run(self.append_row(sheet_name, row_data))

    def sync_read_sheet(self, sheet_name: str) -> list[dict]:
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
        return asyncio.run(self.read_sheet(sheet_name))


# Instance globale
mcp_sheets_client = MCPSheetsClient()
