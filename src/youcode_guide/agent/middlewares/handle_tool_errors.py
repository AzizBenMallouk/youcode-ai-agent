from collections.abc import Callable

from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest


@wrap_tool_call
def handle_tool_errors(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> ToolMessage:
    try:
        return handler(request)

    except Exception:
        return ToolMessage(
            content=(
                "Une erreur technique empêche l'exécution de cette "
                "opération. N'annonce pas que l'opération a réussi. "
                "Propose au visiteur de réessayer ou de contacter "
                "un responsable."
            ),
            tool_call_id=request.tool_call["id"],
        )