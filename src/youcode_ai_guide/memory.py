from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)


_history_store: dict[
    str,
    InMemoryChatMessageHistory,
] = {}


def get_session_history(
    session_id: str,
) -> BaseChatMessageHistory:
    if session_id not in _history_store:
        _history_store[session_id] = (
            InMemoryChatMessageHistory()
        )

    return _history_store[session_id]


def clear_session_history(
    session_id: str,
) -> None:
    history = get_session_history(
        session_id
    )

    history.clear()


def delete_session(
    session_id: str,
) -> None:
    _history_store.pop(
        session_id,
        None,
    )