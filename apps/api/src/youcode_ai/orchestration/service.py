from langchain_core.messages import (
    HumanMessage,
)

from youcode_ai.agents.support.schemas import (
    SupportWorkflowResponse,
)
from youcode_ai.orchestration.graph import (
    get_youcode_graph,
)


class YouCodeOrchestrationService:
    def __init__(self) -> None:
        self.graph = get_youcode_graph()

    def invoke(
        self,
        *,
        message: str,
        session_id: str,
    ) -> SupportWorkflowResponse:
        normalized_message = message.strip()
        normalized_session_id = (
            session_id.strip()
        )

        if not normalized_message:
            raise ValueError(
                "Message cannot be empty."
            )

        if not normalized_session_id:
            raise ValueError(
                "Session ID cannot be empty."
            )

        result = self.graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            normalized_message
                        )
                    )
                ],
                "session_id": (
                    normalized_session_id
                ),
            },
            config=self._create_config(
                normalized_session_id
            ),
        )

        return self._extract_response(
            result
        )

    async def ainvoke(
        self,
        *,
        message: str,
        session_id: str,
    ) -> SupportWorkflowResponse:
        normalized_message = message.strip()
        normalized_session_id = (
            session_id.strip()
        )

        if not normalized_message:
            raise ValueError(
                "Message cannot be empty."
            )

        if not normalized_session_id:
            raise ValueError(
                "Session ID cannot be empty."
            )

        result = await self.graph.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            normalized_message
                        )
                    )
                ],
                "session_id": (
                    normalized_session_id
                ),
            },
            config=self._create_config(
                normalized_session_id
            ),
        )

        return self._extract_response(
            result
        )

    @staticmethod
    def _create_config(
        session_id: str,
    ) -> dict:
        return {
            "configurable": {
                "thread_id": session_id,
            }
        }

    @staticmethod
    def _extract_response(
        result: dict,
    ) -> SupportWorkflowResponse:
        response_data = result.get(
            "final_response"
        )

        if response_data is None:
            raise RuntimeError(
                "The orchestration graph did "
                "not produce a final response."
            )

        return (
            SupportWorkflowResponse
            .model_validate(
                response_data
            )
        )