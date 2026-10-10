# LLM sessions and memory

In this example we use the `LLMSessionsClient` (`platform.llm_session`) to manage conversation sessions and
memory. A session holds the messages of a conversation with a model, so an application can keep the history
across requests. Memory stores key/value data for a user, either within a session or across all of the user's
sessions.

| File            | What it does                                                                            |
|-----------------|-----------------------------------------------------------------------------------------|
| `example_5.py`  | Creates a session for user `123`, adds and reads messages, saves and reads memory, then deletes the session and the memory |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`

## Running the example

```bash
python examples/intro/example_5/example_5.py
```

## Walkthrough

### 1. Create and list sessions

`platform.llm_session.get_or_create_session(request=CreateLLMSessionRequest(user_id="123"))` returns a
session for the user, creating one if needed. `list_sessions(request=ListLLMSessionsRequest(user_id="123"))`
lists all the user's sessions.

### 2. Add and get messages

`add_messages_to_session(...)` appends `LLMMessage` objects to a session. Every message has a `role`
(`user`, `system` or `assistant`), its `content` and a `timestamp`.

`get_messages(...)` reads the session's messages back, with `limit` and `offset` for pagination. The example
asks for up to 10 messages starting at offset 5, so in a new session with only the two messages above nothing
is returned; use `offset=0` to read them back.

### 3. Memory

Memory is addressed by user, session and key:

- `get_memory(...)` reads the value stored under a key. The example reads `some-key` before saving it.
- `save_memory(...)` stores a value (`My-value`) under the key.

### 4. Clean up

- `delete_session(...)` deletes the session
- `delete_memory(...)` deletes a key from the session's memory
- `clear_user_memory(...)` deletes all the memory of a user
