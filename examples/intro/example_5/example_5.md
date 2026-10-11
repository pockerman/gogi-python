# Sessions, context and memory

In this example the `LLMSessionsClient` (`platform.llm_session`) keeps the conversation of a user planning a
cycling holiday with an assistant. The session service stores the conversation and the facts saved about the
user, and assembles a long conversation into a token budget for the next model call.

## Architecture

```
example_5.py ──gRPC──► gateway ──► session service ──► Postgres (sessions, messages, memories, summaries)
                                          └──gRPC──► model service (summaries, if configured)
```

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`

No model is needed. If the platform's session service has a summary model configured
(`GOGI_SESSIONS_SUMMARY_PROVIDER` and `GOGI_SESSIONS_SUMMARY_MODEL`), the `summarize` step shows a summary;
otherwise it truncates and says so.

## Running the example

```bash
python examples/intro/example_5/example_5.py
```

## Walkthrough

### 1. Sessions and messages

`get_or_create_session` with a `session_id` the application chooses creates the session the first time, and
resumes it afterwards. The response's `created` says which happened. A session that belongs to another user is
never returned.

`add_messages_to_session` stores the whole planning conversation in one call, all of it or none:

- a system prompt;
- questions and answers;
- an assistant message that calls a route-planning tool, with no content of its own;
- the tool's result, linked to the call by its id.

`get_messages` without a strategy reads the history back page by page, oldest first, with `limit` and `offset`.

### 2. Memories

`save_memory` saves facts about the user. Values are any JSON value: the bike is a dict, the daily distance a
number. The trip dates are saved for this session only, with `session_id`; the others hold in every session.

To update a memory safely, the example passes the `updated_at` it read as `expected_updated_at`. The first update
succeeds. The second, based on the same stale read, fails with `ABORTED`, since the memory changed in between.

`get_memory` returns every memory. `memories` maps keys to values, and `entries` says which scope each one
belongs to.

### 3. Context strategies

`get_messages` with a `strategy` assembles the context of the next model call within `token_budget` estimated
tokens. The budgets here are small, to make the effects visible on a short conversation.

- **truncate** keeps the system prompt and the most recent messages that fit. `omitted_count` says how many were
  left out. The context never starts with a tool result whose call it left out.
- **summarize** replaces the older messages with a summary, written by the platform's summary model and kept
  for later requests. `summary_focus` says what the summary must keep. Without a summary model, it truncates and
  explains why in `notes`.
- **hierarchical** puts the user's memories first, those of every session and of this one, then the summary,
  then the recent messages.

The response's `strategy` says what was applied, and `estimated_tokens` how much of the budget it took.

### 4. Clean up

`list_sessions` lists the user's sessions, most recently active first, with their message counts.
`delete_session` with `delete_memories=True` deletes the session, its messages and the trip's memories; the
user's own memories stay. `clear_user_memory` then deletes those too.

## Driver code

The complete code of the example, `example_5.py`:

```python
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
```
