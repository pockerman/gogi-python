"""This example illustrates the LLMSessionsClient in gogi, with a user planning a cycling
holiday with an assistant:

- Creates a session, with an id the application chooses, and resumes it
- Stores a conversation, tool calls and tool results included, and reads it back page by page
- Saves facts about the user as memories, for every session or for one, and guards an update
  against a concurrent change
- Assembles the context of the next model call within a token budget: truncation, a summary
  of the older messages, and memories first
- Lists the user's sessions, then deletes the session with its memories

See example_5.md for a discussion of the example.
"""

import uuid

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models import (
    AddMessagesToLLMSessionRequest,
    ClearUserLLMSessionMemoryRequest,
    CreateLLMSessionRequest,
    DeleteLLMSessionRequest,
    GetLLMSessionMemoryRequest,
    GetMessagesFromLLMSessionRequest,
    ListLLMSessionsRequest,
    LLMMessage,
    LLMToolCall,
    SaveLLMSessionMemoryRequest,
    ToolCallFunction,
)

USER = f"example-5-cyclist-{uuid.uuid4().hex[:6]}"
SESSION = f"{USER}-alps"


def conversation() -> list[LLMMessage]:
    """A planning conversation: a system prompt, questions and answers, and a tool call"""
    route = LLMToolCall(
        idx="call-route-1",
        tool_type="function",
        function=ToolCallFunction(name="plan_route", arguments='{"from": "Innsbruck", "to": "Bolzano"}'),
    )
    messages = [
        LLMMessage(role="system", content="You help people plan cycling holidays. Be concise."),
        LLMMessage(role="user", content="I want to ride from Innsbruck to Bolzano in June. Is that doable in a week?"),
        LLMMessage(role="assistant", content="Yes. It's about 300 km with the Brenner Pass; a week leaves rest days."),
        LLMMessage(role="user", content="I ride a gravel bike and manage about 70 km a day. Which route?"),
        LLMMessage(role="assistant", tool_calls=[route]),
        LLMMessage.tool_result(route, '{"km": 286, "climb_m": 3400, "stages": 5}'),
        LLMMessage(role="assistant", content="The Brenner cycle path: 286 km, 3400 m of climbing, in 5 stages."),
    ]
    for day in range(1, 6):
        messages += [
            LLMMessage(role="user", content=f"Where should I sleep after stage {day}?"),
            LLMMessage(role="assistant", content=f"After stage {day}, a guesthouse in the valley town is easiest."),
        ]
    return messages


def sessions_and_messages(platform: Gogi) -> None:
    rich_print(Rule("Sessions and messages"))

    # the application chooses the session id, e.g. one per trip; a new id creates the session
    session = platform.llm_session.get_or_create_session(CreateLLMSessionRequest(user_id=USER, session_id=SESSION))
    rich_print(f"Session {session.session_id}: created={session.created}")

    # the same id resumes it
    session = platform.llm_session.get_or_create_session(CreateLLMSessionRequest(user_id=USER, session_id=SESSION))
    rich_print(f"Session {session.session_id}: created={session.created}")

    # all the messages of the conversation are stored together, or none of them
    added = platform.llm_session.add_messages_to_session(
        AddMessagesToLLMSessionRequest(session_id=SESSION, messages=conversation())
    )
    rich_print(f"Added {added.message_count} messages; the session has {added.total_count}")

    # without a strategy, the history comes back page by page, oldest first
    page = platform.llm_session.get_messages(GetMessagesFromLLMSessionRequest(session_id=SESSION, limit=3, offset=3))
    rich_print(f"Messages 4 to 6 of {page.total_count}:")
    for message in page.messages:
        detail = message.content or ", ".join(f"calls {call.function.name}" for call in message.tool_calls)
        rich_print(f"  {message.role}: {detail}")


def memories(platform: Gogi) -> None:
    rich_print(Rule("Memories"))

    # facts about the user, for every session; values are any JSON value
    platform.llm_session.save_memory(
        SaveLLMSessionMemoryRequest(user_id=USER, key="bike", value={"type": "gravel", "tyres_mm": 42})
    )
    saved = platform.llm_session.save_memory(SaveLLMSessionMemoryRequest(user_id=USER, key="daily_km", value=70))

    # a fact for this trip only
    platform.llm_session.save_memory(
        SaveLLMSessionMemoryRequest(user_id=USER, key="dates", value=["2027-06-12", "2027-06-19"], session_id=SESSION)
    )

    # an update based on what was read; it fails if the memory changed in between
    read_at = saved.entry.updated_at
    platform.llm_session.save_memory(
        SaveLLMSessionMemoryRequest(user_id=USER, key="daily_km", value=80, expected_updated_at=read_at)
    )
    try:
        platform.llm_session.save_memory(
            SaveLLMSessionMemoryRequest(user_id=USER, key="daily_km", value=60, expected_updated_at=read_at)
        )
    except grpc.RpcError as e:
        rich_print(f"A save based on a stale read fails: {e.code().name}")

    memory = platform.llm_session.get_memory(GetLLMSessionMemoryRequest(user_id=USER))
    rich_print(f"Memories: {memory.memories}")
    for entry in memory.entries:
        rich_print(f"  {entry.key} ({'session ' + entry.session_id if entry.session_id else 'every session'})")


def context_strategies(platform: Gogi) -> None:
    rich_print(Rule("Context strategies"))

    for strategy, budget in [("truncate", 120), ("summarize", 160), ("hierarchical", 420)]:
        context = platform.llm_session.get_messages(
            GetMessagesFromLLMSessionRequest(
                session_id=SESSION, strategy=strategy, token_budget=budget, summary_focus="distances, dates and stops"
            )
        )
        rich_print(
            f"[bold]{strategy}[/bold] (budget {budget}): applied {context.strategy}, "
            f"{len(context.messages)} messages, ~{context.estimated_tokens} tokens, {context.omitted_count} left out"
        )
        for message in context.messages[:3]:
            first_line = (message.content or "").splitlines()[0] if message.content else "(tool call)"
            rich_print(f"  {message.role}: {first_line}")
        for note in context.notes:
            rich_print(f"  note: {note}")


def clean_up(platform: Gogi) -> None:
    rich_print(Rule("Clean up"))

    listed = platform.llm_session.list_sessions(ListLLMSessionsRequest(user_id=USER))
    for session in listed.sessions:
        rich_print(f"Session {session.session_id}: {session.message_count} messages, last active {session.updated_at}")

    # the trip's memories go with the session; the user's own stay
    platform.llm_session.delete_session(DeleteLLMSessionRequest(session_id=SESSION, delete_memories=True))
    left = platform.llm_session.get_memory(GetLLMSessionMemoryRequest(user_id=USER))
    rich_print(f"Memories left after deleting the session: {sorted(left.memories)}")

    cleared = platform.llm_session.clear_user_memory(ClearUserLLMSessionMemoryRequest(user_id=USER))
    rich_print(f"Cleared {cleared.count} memories of the user")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    sessions_and_messages(platform)
    memories(platform)
    context_strategies(platform)
    clean_up(platform)
