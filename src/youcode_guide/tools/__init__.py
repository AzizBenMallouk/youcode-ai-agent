from langchain_core.tools import BaseTool

from youcode_guide.rag.service import (
    create_rag_service,
)
from youcode_guide.registration.service import (
    create_registration_service,
)
from youcode_guide.tools.access_support import (
    create_access_support_tool,
)
from youcode_guide.tools.knowledge import (
    create_knowledge_tool,
)
from youcode_guide.tools.registration import (
    create_registration_tool,
)
from youcode_guide.tools.test_reschedule import (
    create_test_reschedule_tool,
)
from youcode_guide.tools.waitlist import (
    create_waitlist_tool,
)
from youcode_guide.visitor_requests.service import (
    create_visitor_request_service,
)


def create_youcode_tools() -> list[BaseTool]:
    rag_service = create_rag_service()

    registration_service = (
        create_registration_service()
    )

    visitor_request_service = (
        create_visitor_request_service()
    )

    return [
        create_knowledge_tool(
            rag_service
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