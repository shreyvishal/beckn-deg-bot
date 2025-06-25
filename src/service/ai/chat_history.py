from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

chat_history = {
    "default-session": InMemoryChatMessageHistory()
}

def get_chat_history(session_id: str = "default-session"):
    if session_id not in chat_history:
        chat_history[session_id] = InMemoryChatMessageHistory()
    return chat_history[session_id]


def with_session_memory(chain, memory_key="chat_history"):
    return RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_chat_history,
        input_messages_key="input",
        history_messages_key=memory_key,
    )

