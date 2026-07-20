from langchain_core.tools import BaseTool

from youcode_guide.metier.retriever.retriever import (
    create_parent_child_retriever,
)
from youcode_guide.metier.services.registration_service import (
    create_registration_service,
)
from youcode_guide.metier.services.visitor_request_service import (
    create_visitor_request_service,
)
from youcode_guide.metier.services.knowledge_gap_service import (
    create_knowledge_gap_service,
)

from youcode_guide.agent.tools.support_tool_factory import (
    create_access_support_tool,
)
from youcode_guide.agent.tools.knowledge_tool_factory import (
    create_knowledge_tool,
)
from youcode_guide.agent.tools.registration_status_tool_factory import (
    create_registration_tool,
)
from youcode_guide.agent.tools.test_reschedule_tool_factory import (
    create_test_reschedule_tool,
)
from youcode_guide.agent.tools.newsletter_tool_factory import (
    create_waitlist_tool,
)
from youcode_guide.agent.tools.report_knowledge_gap_tool_factory import (
    create_report_knowledge_gap_tool,
)


def create_youcode_tools() -> list[BaseTool]:
    retriever_service = (
        create_parent_child_retriever()
    )

    knowledge_gap_service = (
        create_knowledge_gap_service()
    )

    registration_service = (
        create_registration_service()
    )

    visitor_request_service = (
        create_visitor_request_service()
    )


    return [
        create_knowledge_tool(
            retriever_service
        ),
        create_report_knowledge_gap_tool(
            knowledge_gap_service,
        ),
        create_registration_tool(
            registration_service
        ),
        create_waitlist_tool(
            visitor_request_service
        ),
        create_access_support_tool(
            visitor_request_service
        ),
        create_test_reschedule_tool(
            visitor_request_service
        ),
    ]