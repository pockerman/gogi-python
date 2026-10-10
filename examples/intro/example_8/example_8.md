# Tool calling

In this example a model calls the tools the Gogi platform manages. Example 6 registered a clinic's tools and
executed them directly; here the model decides which tools to call and with which arguments, and the
application runs the agent loop: it gives the model the tools, executes the calls the model makes through the
platform, and gives the results back to the model until it answers.

The example uses the `LLMModelsClient` (`platform.llm_clients`) to run the model and the `LLMToolsClient`
(`platform.tools`) to discover and execute the tools.

## Architecture

```
                 ┌─gRPC─► gateway ──► model service ──► OpenAI / Anthropic / Ollama
example_8.py ────┤
                 └─gRPC─► gateway ──► tools service ──HTTP + credential──► tool_server.py
```

The model only sees the tools' definitions; it never reaches the tools, and the application never sees their
credentials.

## Prerequisites

- Everything example 6 needs, and example 6 run once, so that the clinic's tools are registered
- `tool_server.py` of example 6 running
- A model that supports tool calling, with the platform able to call it: by default OpenAI's `gpt-4o-mini`, so
  the model service needs `OPENAI_API_KEY`

The example's settings:

| Variable                        | Default                                | Meaning                                              |
|---------------------------------|----------------------------------------|------------------------------------------------------|
| `GOGI_EXAMPLE_PROVIDER`         | `openai`                               | The provider of the model: `openai`, `anthropic` or `ollama` |
| `GOGI_EXAMPLE_MODEL`            | `gpt-4o-mini`                          | The model, e.g. `claude-opus-5-5` for Anthropic      |
| `GOGI_EXAMPLE_OLLAMA_ENDPOINT`  | `http://host.docker.internal:11434/v1` | Where the model service reaches Ollama; the example registers the model, as example 3 does |
| `GOGI_EXAMPLE_AUTO_CONFIRM`     | (none)                                 | `1` answers every confirmation with yes, e.g. to run the example unattended |

Small local models call tools unreliably. Through Ollama, `mistral` (7B) often writes its tool calls as text
instead of making them, so the loop ends with an answer that the tools did not back. With streaming, Ollama
returns the tool calls of such models as text too. Use a hosted model, or a local one trained for tool calling.

## Running the example

```bash
python examples/intro/example_8/example_8.py
```

With Anthropic's model:

```bash
GOGI_EXAMPLE_PROVIDER=anthropic GOGI_EXAMPLE_MODEL=claude-opus-5-5 python examples/intro/example_8/example_8.py
```

## Walkthrough

### 1. The tools for the model

```python
tools, tool_names = platform.tools.build_model_tools(namespace="healthcare.*", version_constraint="^1.0.0")
```

`build_model_tools` discovers the tools and converts them into the function definitions a model takes. Model
providers do not accept dots in function names, so `healthcare.scheduling.book_appointment` becomes
`healthcare__scheduling__book_appointment`. `tool_names` maps each function name back to the tool, with the
version the model was given, e.g. `healthcare.scheduling.book_appointment@1.0.0`: version 2 of the booking tool
takes other arguments, so the model must get, and the platform must run, version 1.

### 2. The agent loop

```python
response = platform.llm_clients.run(LLMRunRequest(config=config, messages=messages, tools=tools))
messages.append(response.to_message())

if not response.tool_calls:
    ...  # the model answered

results = platform.tools.execute_tool_calls(response.tool_calls, tool_names, session_id=SESSION_ID, confirm=confirm)
messages.extend(results)
```

Each round:

1. The model gets the conversation and the tools. If it calls tools, `finish_reason` is `tool_calls` and
   `tool_calls` has the calls, each with an id, a function name and its arguments as JSON
2. `response.to_message()` is the model's message with its calls; it is part of the conversation, before the
   results
3. `execute_tool_calls` runs each call through the platform, which validates the arguments, injects the
   tool's credential and applies its limits, and returns a `tool` message per call: its `tool_call_id` is the
   call's id and its content the result. A failed call is a result too, `{"error": ...}`, so that the model can
   react, e.g. try another slot
4. The loop runs the model again, until it answers without calling tools, or gives up after `MAX_TURNS`
   rounds

A model may call several tools at once: here it books the slot and verifies the insurance in the same round.

The conversation is the same for every provider: the platform uses OpenAI's format and translates it, e.g. tool
calls into Anthropic's `tool_use` blocks and results into `tool_result` blocks, and Anthropic's stop reason
`tool_use` into the finish reason `tool_calls`.

### 3. Confirmation

The booking tool requires confirmation: the platform refuses to run it unless the call is `confirmed`.
`execute_tool_calls` asks `confirm` about each call, and the example asks a person about the calls of tools
that require confirmation:

```
The model wants to call healthcare.scheduling.book_appointment with {"patient_id": "p-42", "slot": "2026-11-02T09:00"}. Allow it? [y/N]
```

If the person declines, the model gets the error as the result of the call and can tell the patient.

### 4. Streaming

`run_stream` streams the text of the answer as it is generated. The tool calls arrive complete, with the
finish reason, in the last chunk:

```python
for chunk in platform.llm_clients.run_stream(request):
    if chunk.finish_reason is not None:
        for call in chunk.tool_calls:
            ...
```

## Expected output

With a model that calls the tools, the output looks like this (the booking id changes on every run):

```
Tools for the model ['healthcare.billing.verify_insurance@1.0.0', 'healthcare.scheduling.book_appointment@1.0.0', 'healthcare.scheduling.check_availability@1.0.0']
Turn 1: the model calls healthcare__scheduling__check_availability {"clinic_id": "c-1", "date": "2026-11-02"}
Result of healthcare__scheduling__check_availability: {"clinic_id": "c-1", "date": "2026-11-02", "slots": ["2026-11-02T09:00", "2026-11-02T11:30", "2026-11-02T15:00"]}
Turn 2: the model calls healthcare__scheduling__book_appointment {"patient_id": "p-42", "slot": "2026-11-02T09:00"}
Turn 2: the model calls healthcare__billing__verify_insurance {"patient_id": "p-42", "procedure_code": "99213"}
The model wants to call healthcare.scheduling.book_appointment with {"patient_id": "p-42", "slot": "2026-11-02T09:00"}. Allow it? [y/N] y
Result of healthcare__scheduling__book_appointment: {"booking_id": "bk-459ca603", "patient_id": "p-42", "slot": "2026-11-02T09:00"}
Result of healthcare__billing__verify_insurance: {"patient_id": "p-42", "procedure": "99213", "covered_percent": 80}
───────────────────── The model's answer ─────────────────────
...
```

## Driver code

The complete code of the example, `example_8.py`:

```python
"""This example illustrates tool calling: a model calls the tools registered with the
platform, and the platform runs them. It uses the clinic's tools of example 6:

- Discovers the tools and gives them to the model as function definitions
- Runs the agent loop: the model calls tools, the platform executes them with their
  credentials, and their results go back to the model until it answers
- Asks a person to confirm the calls of tools that require confirmation
- Streams a response with tool calls, which arrive complete in the last chunk

Run example_6.py first, to register the tools, and keep tool_server.py running.
See example_8.md for a discussion of the example.
"""

import os
import uuid

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models import (
    LLMCapabilities,
    LLMMessage,
    LLMModelInfo,
    LLMRegisterRequest,
    LLMRunRequest,
    LLMRunRequestConfig,
    LLMToolCall,
)

# the model that calls the tools; it must support tool calling. The default is OpenAI's;
# "anthropic" with "claude-opus-5-5" works the same, as does a model served by Ollama
PROVIDER = os.environ.get("GOGI_EXAMPLE_PROVIDER", "openai")
MODEL = os.environ.get("GOGI_EXAMPLE_MODEL", "gpt-4o-mini")

# where the model service reaches Ollama, if PROVIDER is "ollama"
OLLAMA_ENDPOINT = os.environ.get("GOGI_EXAMPLE_OLLAMA_ENDPOINT", "http://host.docker.internal:11434/v1")

# answer every confirmation with yes, e.g. to run the example unattended
AUTO_CONFIRM = os.environ.get("GOGI_EXAMPLE_AUTO_CONFIRM", "") == "1"

# the model gives up after this many rounds of tool calls
MAX_TURNS = 6

# rate limits per session, e.g. of bookings, count the calls of this conversation
SESSION_ID = f"example-8-{uuid.uuid4().hex[:8]}"

SYSTEM_PROMPT = (
    "You are the scheduling assistant of a clinic. Use the tools to answer; never make up "
    "slots, bookings or coverage. Be brief."
)
QUESTION = (
    "I am patient p-42. Book me the first free slot at clinic c-1 on 2026-11-02, and tell me "
    "whether my insurance covers procedure 99213."
)


def register_ollama_model(platform: Gogi) -> None:
    # as in example 3: a model served by Ollama is added by registering it
    platform.llm_clients.register_llm(
        LLMRegisterRequest(
            info=LLMModelInfo(
                name=MODEL,
                provider="ollama",
                capabilities=LLMCapabilities(
                    context_window=32_000,
                    supports_vision=False,
                    supports_tools=True,
                    supports_streaming=True,
                    supports_json_mode=True,
                ),
            ),
            endpoint=OLLAMA_ENDPOINT,
            health_check="/api/version",
            adapter_type="ollama",
        )
    )


def tools_requiring_confirmation(platform: Gogi) -> set[str]:
    tools = platform.tools.discover(namespace="healthcare.*", version_constraint="^1.0.0")
    return {tool.name for tool in tools if tool.behavior and tool.behavior.requires_confirmation}


def run_agent(platform: Gogi) -> None:
    # The tools of the clinic as function definitions. Version 2 of book_appointment
    # takes other arguments, so the model gets, and the platform runs, version 1
    tools, tool_names = platform.tools.build_model_tools(namespace="healthcare.*", version_constraint="^1.0.0")
    if not tools:
        rich_print("[red]No tools found: run example_6.py first[/red]")
        return
    rich_print(f"Tools for the model {list(tool_names.values())}")

    needs_confirmation = tools_requiring_confirmation(platform)

    def confirm(tool_call: LLMToolCall) -> bool:
        tool = tool_names.get(tool_call.function.name, "").partition("@")[0]
        if tool not in needs_confirmation:
            return False
        question = f"The model wants to call {tool} with {tool_call.function.arguments}. Allow it? [y/N] "
        if AUTO_CONFIRM:
            rich_print(f"{question}y")
            return True
        return input(question).strip().lower() == "y"

    messages = [
        LLMMessage(role="system", content=SYSTEM_PROMPT),
        LLMMessage(role="user", content=QUESTION),
    ]
    config = LLMRunRequestConfig(provider=PROVIDER, model=MODEL, max_tokens=2000)

    for turn in range(MAX_TURNS):
        response = platform.llm_clients.run(LLMRunRequest(config=config, messages=messages, tools=tools))
        # the model's message, with its tool calls, is part of the conversation
        messages.append(response.to_message())

        if not response.tool_calls:
            rich_print(Rule("The model's answer"))
            rich_print(response.content)
            rich_print(f"Finish reason {response.finish_reason}, token usage {response.token_usage}")
            return

        for call in response.tool_calls:
            rich_print(f"Turn {turn + 1}: the model calls {call.function.name} {call.function.arguments}")

        # the platform runs the tools; their results, failures included, go back to the model
        results = platform.tools.execute_tool_calls(
            response.tool_calls, tool_names, session_id=SESSION_ID, confirm=confirm
        )
        for result in results:
            rich_print(f"Result of {result.name}: {result.content}")
        messages.extend(results)

    rich_print(f"[red]No answer after {MAX_TURNS} turns[/red]")


def run_streamed(platform: Gogi) -> None:
    tools, _ = platform.tools.build_model_tools(namespace="healthcare.scheduling", read_only=True)
    request = LLMRunRequest(
        config=LLMRunRequestConfig(provider=PROVIDER, model=MODEL, max_tokens=2000),
        messages=[LLMMessage(role="user", content="Which slots are free at clinic c-1 on 2026-11-02?")],
        tools=tools,
    )

    for chunk in platform.llm_clients.run_stream(request):
        if chunk.token:
            print(chunk.token, end="", flush=True)
        # the tool calls arrive complete, with the finish reason, in the last chunk
        if chunk.finish_reason is not None:
            print()
            rich_print(f"Finish reason {chunk.finish_reason}")
            for call in chunk.tool_calls:
                rich_print(f"Tool call {call.function.name} {call.function.arguments}")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    if PROVIDER == "ollama":
        register_ollama_model(platform)

    try:
        rich_print(Rule(f"Agent loop with {PROVIDER} / {MODEL}"))
        run_agent(platform)

        rich_print(Rule("Streamed tool calls"))
        run_streamed(platform)
    except (ValueError, grpc.RpcError) as error:
        # e.g. the provider's API key is not set, or the model is unknown
        logger.error(f"Request to {PROVIDER}/{MODEL} failed: {error}")
```
