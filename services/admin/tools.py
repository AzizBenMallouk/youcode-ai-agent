import json
import logging
from typing import Any
from langchain_core.tools import tool
from shared.infrastructure.database.connection import database_session
from shared.infrastructure.database.tables.visitor_request import VisitorRequest
from shared.mcp.client import call_agent_tool
from shared.core.config import settings

logger = logging.getLogger(__name__)

@tool("get_visitor_requests")
def get_visitor_requests() -> str:
    """
    Récupère toutes les requêtes de support depuis la base de données.
    Retourne les requêtes sous forme de chaîne JSON.
    Utile pour consulter les demandes des visiteurs ou pour préparer un rapport.
    """
    data = []
    with database_session() as db:
        requests = db.query(VisitorRequest).all()
        for req in requests:
            data.append({
                "id": str(req.id),
                "email": req.email,
                "campus": req.campus,
                "intent": req.intent,
                "first_name": req.first_name,
                "last_name": req.last_name,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "reference": req.reference
            })
            
    if not data:
        return json.dumps({"message": "La base de données est vide."})
        
    return json.dumps(data)

@tool("generate_report_via_mcp")
async def generate_report_via_mcp(data_json: str, sheet_title: str = "Rapport_Admin_Export") -> str:
    """
    Génère un rapport Google Sheets à partir de données JSON en utilisant le serveur sheet-gmcp.
    Prend en paramètre une chaîne JSON (data_json) et optionnellement un titre (sheet_title).
    Retourne le lien vers le rapport Google Sheet généré.
    """
    target_url = getattr(settings, "sheet_gmcp_url", "http://sheet-gmcp:8004")
    
    try:
        result = await call_agent_tool(
            agent_base_url=target_url,
            tool_name="generate_admin_report",
            sheet_title=sheet_title,
            data_json=data_json
        )
        return f"Rapport généré avec succès. Lien: {result}"
    except Exception as e:
        logger.error(f"Failed to generate report via MCP: {e}")
        return f"Erreur lors de la génération du rapport Excel: {str(e)}"
