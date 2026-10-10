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
