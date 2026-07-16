from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
)
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)


class ConversationMemory:
    def __init__(
        self,
        max_messages: int = 12,
    ) -> None:
        self.max_messages = max_messages

        self._sessions: dict[
            str,
            InMemoryChatMessageHistory,
        ] = {}

    def get_history(
        self,
        session_id: str,
    ) -> InMemoryChatMessageHistory:
        if session_id not in self._sessions:
            self._sessions[session_id] = (
                InMemoryChatMessageHistory()
            )

        return self._sessions[session_id]

    def get_messages(
        self,
        session_id: str,
    ) -> list[BaseMessage]:
        history = self.get_history(session_id)

        return list(
            history.messages[
                -self.max_messages:
            ]
        )

    def add_turn(
        self,
        session_id: str,
        human_content: str,
        ai_content: str,
    ) -> None:
        history = self.get_history(session_id)

        history.add_message(
            HumanMessage(
                content=human_content
            )
        )

        history.add_message(
            AIMessage(
                content=ai_content
            )
        )

        self._trim(session_id)

    def _trim(
        self,
        session_id: str,
    ) -> None:
        history = self.get_history(session_id)

        if (
            len(history.messages)
            <= self.max_messages
        ):
            return

        history.messages = history.messages[
            -self.max_messages:
        ]

    def clear(
        self,
        session_id: str,
    ) -> None:
        self._sessions.pop(
            session_id,
            None,
        )

    def clear_all(self) -> None:
        self._sessions.clear()