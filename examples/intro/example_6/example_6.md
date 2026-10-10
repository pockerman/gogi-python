# Tools

In this example we use the `LLMToolsClient` (`platform.tools`) to work with tools the Gogi platform manages. A
tool is a capability a model can call, such as booking an appointment. Instead of every application defining
its tools inline and holding their API keys, tools are registered once with the platform and become entities
with a name, versions, an owner and operational metadata. Applications then discover them and call them
through the platform, which validates the arguments, injects the credentials, enforces rate and execution
limits, and stops calling tools that keep failing.

The example follows a clinic: a scheduling team registers tools to check availability and book appointments,
and a billing team a tool to verify insurance.

| File              | What it does                                                                                   |
|-------------------|------------------------------------------------------------------------------------------------|
| `example_6.py`    | Registers the clinic's tools, then discovers, validates and executes them, registers a new major version, builds function definitions for a model, and imports the tools of an MCP server |
| `tool_server.py`  | A small HTTP service that plays the clinic's scheduling and billing systems                    |

## Architecture

```
example_6.py ──gRPC──► gateway ──► tools service ──HTTP + credential──► tool_server.py
                                        │    └──MCP (Streamable HTTP)──► an MCP server
                                        ├──► PostgreSQL (tool registry, async tasks)
                                        └──► credential store (Vault / AWS Secrets Manager)
```

The example never talks to `tool_server.py` directly, and never sees the booking API key.

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051` and the database migrations applied
  (migration `000009` extends the tool registry)
- `tool_server.py` running:

  ```bash
  python examples/intro/example_6/tool_server.py
  ```

- The booking API key in the platform's credential store, as the credential `scheduling-api-prod`. With the
  Docker Compose platform, which uses a Vault dev server:

  ```bash
  docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=gogi-dev-root-token gogi-vault \
    vault kv put secret/gogi/credentials/scheduling-api-prod value=example-api-key
  ```

  `example-api-key` is the key `tool_server.py` expects (`GOGI_EXAMPLE_TOOL_API_KEY`). See the platform's
  `docs/credentials.md` for the credential store.

The example's settings:

| Variable                          | Default                             | Meaning                                       |
|-----------------------------------|-------------------------------------|-----------------------------------------------|
| `GOGI_EXAMPLE_TOOL_SERVER_URL`    | `http://host.docker.internal:8765`  | Where the tools service reaches `tool_server.py`. The default suits the platform in Docker Compose; use `http://localhost:8765` if the tools service runs on the host |
| `GOGI_EXAMPLE_MCP_SERVER_URL`     | (none)                              | An MCP server (Streamable HTTP) to import tools from; the MCP step is skipped without it |
| `GOGI_EXAMPLE_MCP_CREDENTIAL_REF` | (none)                              | The credential the MCP server requires, if any |

## Running the example

```bash
python examples/intro/example_6/example_6.py
```

Registered versions of a tool cannot change, so running the example again reports the tools as already
registered and carries on.

## Walkthrough

### 1. Register tools

`platform.tools.register(...)` adds a version of a tool to the registry. A registration has three parts:

| Part        | Fields                                                     | Used by                                       |
|-------------|------------------------------------------------------------|-----------------------------------------------|
| Identity    | `name`, `version` (default `1.0.0`), `owner`               | The registry: discovery, versions, ownership  |
| Schema      | `description`, `parameters`, `returns`                     | Models, when they decide whether and how to call the tool |
| Operations  | `endpoint`, `credential_ref`, `behavior`, `rate_limits`, `execution_limits`, `cost`, `capabilities`, `tags` | The platform, when it calls the tool |

- `name` is namespaced, `<domain>.<capability area>.<operation>`, e.g. `healthcare.scheduling.book_appointment`,
  so that teams own their namespaces and tools with the same operation name do not clash.
- `parameters` is either a full JSON Schema or, as in the example, a mapping from each parameter to its schema,
  where every parameter is required unless marked `"optional": True`.
- `endpoint` is where the platform calls the tool: it POSTs the arguments as JSON and returns the JSON response.
- `credential_ref` names a credential held by the platform's credential store. The platform sends it to the
  endpoint as a bearer token; the application registering or calling the tool never sees it.
- `behavior` tells the platform how to treat the tool. `check_availability` is read-only and idempotent: it can be
  called freely, and retried if it fails. `book_appointment` changes state, so it is not retried (a retry could
  book twice) and `requires_confirmation`, so it runs only once a person approved the call.
- `rate_limits` caps the calls: `book_appointment` allows 3 bookings per session (a conversation), to prevent the
  "book five appointments just in case" problem.
- `execution_limits` bounds each call: a timeout, the size of the response, and how many times a failed call to an
  idempotent tool is retried. The platform caps them with its own ceilings.

`platform.tools.register_tool(LLMRegisterToolRequest(tool=...))` takes a complete `LLMToolServiceDefinition`
instead of keyword arguments.

### 2. Discover tools

`platform.tools.discover(...)` returns tool definitions, most relevant first:

- by namespace: `namespace="healthcare.scheduling.*"` returns the scheduling tools
- by capability and tag, across namespaces: `capabilities=["insurance", "coverage"]` finds the tools that have
  any of them, scored by how many they have
- `read_only=True` returns only the tools that do not change state
- `version_constraint`, e.g. `^1.0.0`, picks for each tool the latest version that satisfies it

Discovery returns what applications and models need to use a tool, but not its endpoint: tools are called through
the platform. A tool whose calls keep failing is hidden from discovery until it recovers, so that models do not
keep picking it.

### 3. Validate and execute

- `platform.tools.validate(name, arguments)` checks arguments against the tool's parameters without calling it:
  here the missing `date` is reported.
- `platform.tools.execute(name, arguments, session_id=...)` calls the tool and waits for its result.
  `result_json` is the tool's response; `tool_version` the version that ran (the latest unless `version` pins one).

A call that fails returns `success=False` with an `error` the model can reason about, rather than raising: invalid
arguments, a rate limit, a timeout, an error of the tool, or a call that needs confirmation. The first booking is
refused because it is not confirmed; the second, with `confirmed=True`, books the slot. The platform injected the
booking API key, which `tool_server.py` checks.

### 4. Asynchronous execution

`verify_insurance` takes a few seconds. `platform.tools.execute_async(...)` starts the call in the background and
returns a task id at once; `platform.tools.get_task(task_id)` reports its status (`pending`, `running`, then
`succeeded`, `failed` or `timed_out`) and, once done, its result. An application can carry on the conversation
meanwhile.

### 5. Versions

Version `2.0.0` of `book_appointment` adds the required `appointment_type`. That breaks the callers of version 1,
whose arguments lack it, so the registry accepts it only as a new major version: registering it as `1.1.0` is
rejected. Within a major version, a new version cannot remove parameters or add required ones.

Both versions stay in the registry. Discovery with `version_constraint="^1.0.0"` still returns version 1, and the
version 1 arguments are valid for version 1 but not for the latest version. Applications pin a version, or a
constraint, and migrate when they are ready.

### 6. Tools for a model

`platform.tools.build_model_tools(namespace="healthcare.*")` discovers tools and converts them into the function
definitions models take, to pass as the `tools` of an `LLMRunRequest`. Model providers do not accept dots in
function names, so `healthcare.scheduling.book_appointment` becomes `healthcare__scheduling__book_appointment`;
the returned `tool_names` maps the function names back, and `platform.tools.execute_tool_call(tool_call,
tool_names, ...)` runs the tool a model called.

### 7. Import an MCP server

With `GOGI_EXAMPLE_MCP_SERVER_URL` set, `platform.tools.register_mcp_server(...)` connects the platform to an MCP
server and imports its tools into the `devtools.mcp` namespace. The platform is the MCP client for every
application: the tools are discovered and executed like any other, with the server's credential taken from the
credential store and the registration's policy overrides applied (here every imported tool requires
confirmation). If a tool's definition on the server changes, importing the server again registers it as a new
major version, so applications keep the definition they approved.

## Driver code

The complete code of the example, `example_6.py`:

```python
"""This example illustrates the LLMToolsClient in gogi: tools as capabilities the
platform manages. The example registers a clinic's scheduling and billing tools and:

- Discovers tools by namespace, capability, and version constraint
- Validates arguments against a tool's schema before calling it
- Executes tools; the platform injects their credentials, so the example never sees them
- Asks for confirmation before a tool that changes state runs
- Executes a slow tool asynchronously and polls for its result
- Registers a new major version of a tool, while callers pinned to the old one keep it
- Converts the registered tools into function definitions for a model
- Imports the tools of an MCP server, if one is configured

The tools are served by tool_server.py, which must be running.
See example_6.md for a discussion of the example.
"""

import json
import os
import time
import uuid

import grpc
from loguru import logger
from rich import print as rich_print
from rich.rule import Rule

from gogi.gogi import Gogi
from gogi.models.llm.llm_tool_service_definition import LLMToolBehavior
from gogi.models.llm.requests.llm_tools.llm_register_mcp_server_request import (
    LLMRegisterMcpServerRequest,
)

# where the tools service reaches tool_server.py. With the platform in Docker Compose that
# is the host; use http://localhost:8765 if the tools service runs on the host
TOOL_SERVER_URL = os.environ.get("GOGI_EXAMPLE_TOOL_SERVER_URL", "http://host.docker.internal:8765")

# the credential of the booking API, held by the platform's credential store
BOOKING_CREDENTIAL = "scheduling-api-prod"

# an MCP server (Streamable HTTP) to import tools from, e.g. http://host.docker.internal:3000/mcp
MCP_SERVER_URL = os.environ.get("GOGI_EXAMPLE_MCP_SERVER_URL", "")
# the credential the MCP server requires, if any, held by the platform's credential store
MCP_CREDENTIAL_REF = os.environ.get("GOGI_EXAMPLE_MCP_CREDENTIAL_REF", "")

# rate limits per session, e.g. of bookings, count the calls of this run only
SESSION_ID = f"example-6-{uuid.uuid4().hex[:8]}"


def register(platform: Gogi, **tool) -> None:
    # Registered versions cannot change, so running the example again finds them registered
    try:
        response = platform.tools.register(**tool)
        rich_print(f"Registered {response.name}@{response.version}")
    except grpc.RpcError as error:
        if error.code() != grpc.StatusCode.ALREADY_EXISTS:
            raise
        rich_print(f"{tool['name']}@{tool.get('version', '1.0.0')} is already registered")


def register_tools(platform: Gogi) -> None:
    # Tool names are namespaced: <domain>.<capability area>.<operation>
    register(
        platform,
        name="healthcare.scheduling.check_availability",
        description="List the free appointment slots of a clinic on a date, as ISO 8601 times",
        parameters={
            "clinic_id": {"type": "string", "description": "Clinic identifier"},
            "date": {"type": "string", "description": "The date, e.g. 2026-11-02"},
        },
        endpoint=f"{TOOL_SERVER_URL}/availability",
        # read-only and idempotent: it can be called freely, and retried if it fails
        behavior={"is_read_only": True, "is_idempotent": True, "typical_latency_ms": 200},
        execution_limits={"timeout_seconds": 5, "max_retries": 2},
        capabilities=["appointments", "availability"],
        tags=["patient-facing"],
    )

    register(
        platform,
        name="healthcare.scheduling.book_appointment",
        owner="scheduling-team",
        description="Book a free appointment slot for a patient. Returns the booking id",
        parameters={
            "patient_id": {"type": "string", "description": "Patient identifier"},
            "slot": {"type": "string", "description": "A free slot returned by check_availability"},
        },
        endpoint=f"{TOOL_SERVER_URL}/bookings",
        # the platform sends this credential to the endpoint; the example never sees the key
        credential_ref=BOOKING_CREDENTIAL,
        # it changes state: a person confirms each booking, and it is never retried
        behavior={"is_read_only": False, "is_idempotent": False, "requires_confirmation": True},
        # at most 3 bookings per conversation
        rate_limits={"requests_per_session": 3},
        capabilities=["appointments", "booking"],
        tags=["patient-facing"],
    )

    register(
        platform,
        name="healthcare.billing.verify_insurance",
        description="Verify whether a patient's insurance covers a procedure, and the percentage it covers",
        parameters={
            "patient_id": {"type": "string"},
            "procedure_code": {"type": "string", "description": "CPT code of the procedure, e.g. 99213"},
        },
        endpoint=f"{TOOL_SERVER_URL}/coverage",
        behavior={"is_read_only": True, "is_idempotent": True, "typical_latency_ms": 3000},
        execution_limits={"timeout_seconds": 30},
        cost={"estimated_cost_usd": 0.02, "billing_category": "insurance-checks"},
        capabilities=["insurance", "verification"],
        tags=["patient-facing"],
    )


def discover_tools(platform: Gogi) -> None:
    # by namespace: the latest version of every scheduling tool
    for tool in platform.tools.discover(namespace="healthcare.scheduling.*"):
        rich_print(f"{tool.name}@{tool.version}: {tool.description}")

    # by capability, across namespaces, most relevant first
    tools = platform.tools.discover(capabilities=["insurance", "coverage"], tags=["patient-facing"])
    rich_print(f"Insurance tools {[tool.name for tool in tools]}")

    # only the tools that do not change state
    tools = platform.tools.discover(namespace="healthcare.*", read_only=True)
    rich_print(f"Read-only tools {[tool.name for tool in tools]}")


def execute_tools(platform: Gogi) -> None:
    # check the arguments before calling a tool
    validation = platform.tools.validate("healthcare.scheduling.check_availability", {"clinic_id": "c-1"})
    rich_print(f"Validation of incomplete arguments {validation}")

    availability = platform.tools.execute(
        "healthcare.scheduling.check_availability",
        {"clinic_id": "c-1", "date": "2026-11-02"},
        session_id=SESSION_ID,
    )
    rich_print(f"Availability {availability}")
    if not availability.success:
        rich_print("[red]The tool failed: is tool_server.py running, and reachable at TOOL_SERVER_URL?[/red]")
        return
    slot = json.loads(availability.result_json)["slots"][0]

    # A tool that requires confirmation does not run until a person approves the call.
    # A failed call is a result, not an exception, so that it can be given to a model
    booking = platform.tools.execute(
        "healthcare.scheduling.book_appointment",
        {"patient_id": "p-42", "slot": slot},
        session_id=SESSION_ID,
        version="1.0.0",
    )
    rich_print(f"Booking without confirmation {booking}")

    booking = platform.tools.execute(
        "healthcare.scheduling.book_appointment",
        {"patient_id": "p-42", "slot": slot},
        session_id=SESSION_ID,
        version="1.0.0",
        confirmed=True,
    )
    rich_print(f"Booking after confirmation {booking}")

    # a slow tool runs in the background while the application carries on
    task = platform.tools.execute_async(
        "healthcare.billing.verify_insurance", {"patient_id": "p-42", "procedure_code": "99213"}, session_id=SESSION_ID
    )
    rich_print(f"Started task {task}")
    while task.status in ("pending", "running"):
        time.sleep(1)
        task = platform.tools.get_task(task.task_id)
        rich_print(f"Task status {task.status}")
    rich_print(f"Insurance verification {task}")


def new_major_version(platform: Gogi) -> None:
    # Version 2 adds a required parameter, which breaks the callers of version 1, so it must
    # be a new major version: registering it as 1.1.0 is rejected
    register(
        platform,
        name="healthcare.scheduling.book_appointment",
        version="2.0.0",
        owner="scheduling-team",
        description="Book a free appointment slot for a patient, for a type of appointment. Returns the booking id",
        parameters={
            "patient_id": {"type": "string"},
            "slot": {"type": "string"},
            "appointment_type": {"type": "string", "enum": ["consultation", "follow-up", "vaccination"]},
            "notes": {"type": "string", "optional": True},
        },
        endpoint=f"{TOOL_SERVER_URL}/bookings",
        credential_ref=BOOKING_CREDENTIAL,
        behavior={"requires_confirmation": True},
        rate_limits={"requests_per_session": 3},
        capabilities=["appointments", "booking"],
    )

    # applications pinned to version 1 keep getting it
    for constraint in ("^1.0.0", ""):
        tools = platform.tools.discover(namespace="healthcare.scheduling", version_constraint=constraint)
        rich_print(f"Constraint {constraint or 'none'}: {[f'{tool.name}@{tool.version}' for tool in tools]}")

    arguments = {"patient_id": "p-42", "slot": "2026-11-02T09:00"}
    validation = platform.tools.validate("healthcare.scheduling.book_appointment", arguments, version="1.0.0")
    rich_print(f"Valid arguments for version 1.0.0: {validation.valid}")
    validation = platform.tools.validate("healthcare.scheduling.book_appointment", arguments)
    rich_print(f"The same arguments for the latest version {validation}")


def model_tools(platform: Gogi) -> None:
    # The registered tools as the function definitions a model takes, ready to pass as the
    # tools of an LLMRunRequest. Model providers do not accept dots in function names, so the
    # names are mapped; tool_names maps them back for execute_tool_call
    definitions, tool_names = platform.tools.build_model_tools(namespace="healthcare.*")
    for definition in definitions:
        rich_print(definition)
    rich_print(f"Function names {tool_names}")


def import_mcp_server(platform: Gogi) -> None:
    # One registration imports every tool of the MCP server into the namespace; applications
    # then discover and execute them like any other tool
    response = platform.tools.register_mcp_server(
        LLMRegisterMcpServerRequest(
            server_url=MCP_SERVER_URL,
            namespace="devtools.mcp",
            credential_ref=MCP_CREDENTIAL_REF,
            policy_overrides=LLMToolBehavior(requires_confirmation=True),
        )
    )
    rich_print(f"Imported tools {response.imported_tool_names}")
    tools = platform.tools.discover(namespace="devtools.mcp")
    for tool in tools:
        rich_print(f"{tool.name}@{tool.version}: {tool.description}")

    # the policy overrides apply to the imported tools: the first call needs confirmation
    read_only = [tool for tool in tools if tool.behavior and tool.behavior.is_read_only]
    if read_only:
        result = platform.tools.execute(read_only[0].name, session_id=SESSION_ID, confirmed=True)
        rich_print(f"{read_only[0].name} {result}")


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    rich_print(Rule("Registering tools"))
    register_tools(platform)

    rich_print(Rule("Discovering tools"))
    discover_tools(platform)

    rich_print(Rule("Executing tools"))
    execute_tools(platform)

    rich_print(Rule("Versions"))
    new_major_version(platform)

    rich_print(Rule("Tools for a model"))
    model_tools(platform)

    if MCP_SERVER_URL:
        rich_print(Rule("Importing an MCP server"))
        import_mcp_server(platform)
```
