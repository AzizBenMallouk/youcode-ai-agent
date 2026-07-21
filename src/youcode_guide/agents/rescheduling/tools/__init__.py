from langchain_core.tools import BaseTool

from youcode_guide.agents.rescheduling.tools.prepare_rescheduling_request import prepare_rescheduling_request
from youcode_guide.agents.rescheduling.tools.propose_rescheduling_session import propose_rescheduling_session



def create_rescheduling_tools() -> list[BaseTool]:
    return [
        prepare_rescheduling_request,
        propose_rescheduling_session,
    ]
