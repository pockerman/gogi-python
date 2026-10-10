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

## Driver code

The complete code of the example, `example_5.py`:

```python
"""This example illustrates the LLMSessionsClient in gogi.
The client allows users to:

- Create a new session
- List all available sessions
- Add messages to a session
- Get the messages associated with a session
- Delete a sessions


"""

import time

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.models import CreateLLMSessionRequest
from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import (
    AddMessagesToLLMSessionRequest,
)
from gogi.models.llm.requests.llm_session.clear_user_llm_session_memory_request import (
    ClearUserLLMSessionMemoryRequest,
)
from gogi.models.llm.requests.llm_session.delete_llm_session_memory_request import (
    DeleteLLMSessionMemoryRequest,
)
from gogi.models.llm.requests.llm_session.delete_llm_session_request import (
    DeleteLLMSessionRequest,
)
from gogi.models.llm.requests.llm_session.get_llm_session_memory_request import (
    GetLLMSessionMemoryRequest,
)
from gogi.models.llm.requests.llm_session.get_messages_from_llm_session_request import (
    GetMessagesFromLLMSessionRequest,
)
from gogi.models.llm.requests.llm_session.list_llm_session_request import (
    ListLLMSessionsRequest,
)
from gogi.models.llm.requests.llm_session.save_llm_session_memory_request import (
    SaveLLMSessionMemoryRequest,
)

if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # create new session
    create_llm_session_response = platform.llm_session.get_or_create_session(
        request=CreateLLMSessionRequest(user_id="123")
    )
    rich_print(f"Create llm session response {create_llm_session_response}")

    # list the LLM sessions for this user
    list_sessions_response = platform.llm_session.list_sessions(request=ListLLMSessionsRequest(user_id="123"))
    rich_print(f"List llm sessions response {list_sessions_response}")

    # add messages
    messages = [
        LLMMessage(
            role="user",
            content="What's the weather in London today?",
            timestamp=int(time.time()),
        ),
        LLMMessage(
            role="system",
            content="You are a helpful AI assistant.",
            timestamp=int(time.time()),
        ),
    ]
    add_messages_to_session_response = platform.llm_session.add_messages_to_session(
        request=AddMessagesToLLMSessionRequest(session_id=create_llm_session_response.session_id, messages=messages)
    )
    rich_print(f"Add messages to llm sessions response {add_messages_to_session_response}")

    # get the messages
    get_session_messages_response = platform.llm_session.get_messages(
        request=GetMessagesFromLLMSessionRequest(session_id=create_llm_session_response.session_id, limit=10, offset=5)
    )
    rich_print(f"Get messages from llm sessions response {get_session_messages_response}")

    # get the session memeory
    get_memory_response = platform.llm_session.get_memory(
        request=GetLLMSessionMemoryRequest(
            user_id="123", key="some-key", session_id=create_llm_session_response.session_id
        )
    )
    rich_print(f"Get llm session memory response {get_memory_response}")

    save_memory_response = platform.llm_session.save_memory(
        request=SaveLLMSessionMemoryRequest(
            user_id="123", key="some-key", session_id=create_llm_session_response.session_id, value="My-value"
        )
    )
    rich_print(f"Save llm session memory response {save_memory_response}")

    # delete the session
    delete_llm_session_response = platform.llm_session.delete_session(
        request=DeleteLLMSessionRequest(session_id=create_llm_session_response.session_id)
    )
    rich_print(f"Delete llm session response {delete_llm_session_response}")

    # delete memory for the given session
    delete_session_memory_response = platform.llm_session.delete_memory(
        request=DeleteLLMSessionMemoryRequest(
            session_id=create_llm_session_response.session_id, key="some-key", user_id="123"
        )
    )
    rich_print(f"Delete session memeory response {delete_session_memory_response}")

    # delete the user memory
    clear_user_memory_response = platform.llm_session.clear_user_memory(
        request=ClearUserLLMSessionMemoryRequest(user_id="123")
    )
    rich_print(f"Clear user memory response {clear_user_memory_response}")
```
