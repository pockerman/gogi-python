import hashlib
import json
import re
from typing import Any

from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.llm_tools_client_grpc_helpers import (
    LLMToolsClientGRPCHelper,
)
from gogi.models.llm.llm_function_definition import LLMFunctionDefinition
from gogi.models.llm.llm_tool_definition import LLMToolCall, LLMToolDefinition
from gogi.models.llm.llm_tool_service_definition import (
    LLMCostMetadata,
    LLMExecutionLimits,
    LLMRateLimits,
    LLMToolBehavior,
    LLMToolServiceDefinition,
)
from gogi.models.llm.requests.llm_tools.llm_discover_tools_request import (
    LLMDiscoverToolsRequest,
)
from gogi.models.llm.requests.llm_tools.llm_execute_tool_request import (
    LLMExecuteToolRequest,
)
from gogi.models.llm.requests.llm_tools.llm_get_task_request import LLMGetTaskRequest
from gogi.models.llm.requests.llm_tools.llm_register_mcp_server_request import (
    LLMRegisterMcpServerRequest,
)
from gogi.models.llm.requests.llm_tools.llm_register_tool_request import (
    LLMRegisterToolRequest,
)
from gogi.models.llm.requests.llm_tools.llm_validate_tool_request import (
    LLMValidateToolRequest,
)
from gogi.models.llm.responses.llm_tools.llm_discover_tools_response import (
    LLMDiscoverToolsResponse,
)
from gogi.models.llm.responses.llm_tools.llm_execute_tool_async_response import (
    LLMExecuteToolAsyncResponse,
)
from gogi.models.llm.responses.llm_tools.llm_execute_tool_response import (
    LLMExecuteToolResponse,
)
from gogi.models.llm.responses.llm_tools.llm_get_task_response import LLMGetTaskResponse
from gogi.models.llm.responses.llm_tools.llm_register_mcp_server_response import (
    LLMRegisterMcpServerResponse,
)
from gogi.models.llm.responses.llm_tools.llm_register_tool_response import (
    LLMRegisterToolResponse,
)
from gogi.models.llm.responses.llm_tools.llm_validate_tool_response import (
    LLMValidateToolResponse,
)
from gogi.v1 import llm_tool_service_pb2_grpc

# the parameters schema of a tool that takes no arguments
NO_PARAMETERS_SCHEMA = {"type": "object", "properties": {}}

# model providers accept function names of letters, digits, '_' and '-', of up to 64 characters
_MAX_FUNCTION_NAME_LENGTH = 64
_INVALID_FUNCTION_NAME_CHARACTERS = re.compile(r"[^A-Za-z0-9_-]")


def parameters_schema(parameters: dict[str, Any] | None) -> dict[str, Any]:
    """Return the JSON Schema of a tool's parameters.

    ``parameters`` is either a complete object schema (with ``"type": "object"``) or a
    mapping from each parameter's name to its schema, as in::

        {
            "patient_id": {"type": "string", "description": "Patient identifier"},
            "notes": {"type": "string", "optional": True},
        }

    in which case every parameter is required unless it is marked ``"optional": True``.
    """
    if not parameters:
        return dict(NO_PARAMETERS_SCHEMA)
    if parameters.get("type") == "object":
        return parameters

    properties: dict[str, Any] = {}
    required: list[str] = []
    for name, schema in parameters.items():
        schema = dict(schema)
        if not schema.pop("optional", False):
            required.append(name)
        properties[name] = schema
    return {"type": "object", "properties": properties, "required": required}


def model_function_name(tool_name: str) -> str:
    """Return the function name under which a model sees a tool.

    Tool names are namespaced with dots, e.g. ``healthcare.scheduling.book_appointment``, but
    model providers do not accept dots in function names, so they are replaced with ``__``.
    Names longer than providers accept are shortened, keeping them unique with a hash.
    """
    name = _INVALID_FUNCTION_NAME_CHARACTERS.sub("_", tool_name.replace(".", "__"))
    if len(name) > _MAX_FUNCTION_NAME_LENGTH:
        digest = hashlib.sha256(tool_name.encode()).hexdigest()[:8]
        name = name[: _MAX_FUNCTION_NAME_LENGTH - len(digest) - 1] + "_" + digest
    return name


class LLMToolsClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-tools", logger=logger)
        self._grpc_helper = LLMToolsClientGRPCHelper()
        self._stub = llm_tool_service_pb2_grpc.ToolServerStub(self._channel)

    def register_tool(self, request: LLMRegisterToolRequest) -> LLMRegisterToolResponse:
        grpc_request = self._grpc_helper.build_grpc_register_tool_request(request)
        grpc_response = self._stub.RegisterTool(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_register_tool_grpc_response(grpc_response)

    def discover_tools(self, request: LLMDiscoverToolsRequest) -> LLMDiscoverToolsResponse:
        grpc_request = self._grpc_helper.build_grpc_discover_tools_request(request)
        grpc_response = self._stub.DiscoverTools(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_discover_tools_grpc_response(grpc_response)

    def execute_tool(self, request: LLMExecuteToolRequest) -> LLMExecuteToolResponse:
        grpc_request = self._grpc_helper.build_grpc_execute_tool_request(request)
        grpc_response = self._stub.ExecuteTool(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_execute_tool_grpc_response(grpc_response)

    def validate_tool(self, request: LLMValidateToolRequest) -> LLMValidateToolResponse:
        grpc_request = self._grpc_helper.build_grpc_validate_tool_request(request)
        grpc_response = self._stub.ValidateTool(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_validate_tool_grpc_response(grpc_response)

    def execute_tool_async(self, request: LLMExecuteToolRequest) -> LLMExecuteToolAsyncResponse:
        grpc_request = self._grpc_helper.build_grpc_execute_tool_async_request(request)
        grpc_response = self._stub.ExecuteToolAsync(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_execute_tool_async_grpc_response(grpc_response)

    def get_task(self, request: LLMGetTaskRequest | str) -> LLMGetTaskResponse:
        """Get an asynchronous tool call, by its request or its task id."""
        if isinstance(request, str):
            request = LLMGetTaskRequest(task_id=request)
        grpc_request = self._grpc_helper.build_grpc_get_task_request(request)
        grpc_response = self._stub.GetTask(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_get_task_grpc_response(grpc_response)

    def register_mcp_server(self, request: LLMRegisterMcpServerRequest) -> LLMRegisterMcpServerResponse:
        grpc_request = self._grpc_helper.build_grpc_register_mcp_server_request(request)
        grpc_response = self._stub.RegisterMcpServer(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_register_mcp_server_grpc_response(grpc_response)

    # --- Convenience API ---
    #
    # The methods below take keyword arguments instead of request objects.

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any] | None = None,
        *,
        version: str = "1.0.0",
        owner: str = "",
        returns: dict[str, Any] | None = None,
        endpoint: str = "",
        credential_ref: str = "",
        behavior: LLMToolBehavior | dict[str, Any] | None = None,
        rate_limits: LLMRateLimits | dict[str, Any] | None = None,
        cost: LLMCostMetadata | dict[str, Any] | None = None,
        execution_limits: LLMExecutionLimits | dict[str, Any] | None = None,
        capabilities: list[str] | None = None,
        tags: list[str] | None = None,
        required_permissions: list[str] | None = None,
    ) -> LLMRegisterToolResponse:
        """Register a version of a tool with the platform.

        ``name`` is the tool's fully qualified name, e.g. ``healthcare.scheduling.book_appointment``.
        ``parameters`` is the schema of its arguments (see :func:`parameters_schema`), and
        ``endpoint`` is where the platform calls it: the tool's arguments are POSTed to it as JSON.
        ``credential_ref`` names the credential the platform sends to the endpoint, held by the
        platform's credential store; the secret itself never passes through the SDK.

        Registered versions cannot change: to change a tool, register a new version. Within a major
        version, a version must not remove parameters or add required ones.
        """
        tool = LLMToolServiceDefinition(
            name=name,
            version=version,
            owner=owner,
            description=description,
            parameters_json=json.dumps(parameters_schema(parameters)),
            returns_json=json.dumps(returns) if returns else "",
            behavior=LLMToolBehavior.model_validate(behavior) if behavior is not None else None,
            rate_limits=LLMRateLimits.model_validate(rate_limits) if rate_limits is not None else None,
            cost=LLMCostMetadata.model_validate(cost) if cost is not None else None,
            execution_limits=LLMExecutionLimits.model_validate(execution_limits)
            if execution_limits is not None
            else None,
            capabilities=capabilities or [],
            tags=tags or [],
            required_permissions=required_permissions or [],
            endpoint=endpoint,
            credential_ref=credential_ref,
        )
        return self.register_tool(LLMRegisterToolRequest(tool=tool))

    def discover(
        self,
        namespace: str = "",
        capabilities: list[str] | None = None,
        tags: list[str] | None = None,
        read_only: bool = False,
        version_constraint: str = "",
    ) -> list[LLMToolServiceDefinition]:
        """Find tools, most relevant first.

        ``namespace`` selects the tools under it, e.g. ``healthcare.scheduling.*``. ``capabilities``
        and ``tags`` search for tools that have any of them. ``version_constraint``, e.g. ``^1.0.0``,
        selects for each tool its latest version that satisfies it; by default its latest version.
        """
        response = self.discover_tools(
            LLMDiscoverToolsRequest(
                namespace=namespace,
                capabilities=capabilities or [],
                tags=tags or [],
                read_only=read_only,
                version_constraint=version_constraint,
            )
        )
        return response.tools

    def build_model_tools(
        self,
        namespace: str = "",
        capabilities: list[str] | None = None,
        tags: list[str] | None = None,
        read_only: bool = False,
        version_constraint: str = "",
    ) -> tuple[list[LLMToolDefinition], dict[str, str]]:
        """Discover tools and convert them into the function definitions models take.

        Returns the definitions, to pass as the ``tools`` of an ``LLMRunRequest``, and a mapping
        from the function name of each tool, which a model uses in its tool calls, to the tool's
        name (see :func:`model_function_name`). :meth:`execute_tool_call` uses that mapping to run
        the tool a model calls.
        """
        definitions: list[LLMToolDefinition] = []
        tool_names: dict[str, str] = {}
        for tool in self.discover(namespace, capabilities, tags, read_only, version_constraint):
            function_name = model_function_name(tool.name)
            tool_names[function_name] = tool.name
            definitions.append(
                LLMToolDefinition(
                    tool_type="function",
                    function=LLMFunctionDefinition(
                        name=function_name,
                        description=tool.description,
                        parameters_json=tool.parameters_json or json.dumps(NO_PARAMETERS_SCHEMA),
                    ),
                )
            )
        return definitions, tool_names

    def validate(
        self, name: str, arguments: dict[str, Any] | None = None, *, version: str = ""
    ) -> LLMValidateToolResponse:
        """Check arguments against a tool's parameters without calling the tool."""
        return self.validate_tool(
            LLMValidateToolRequest(tool_name=name, arguments_json=json.dumps(arguments or {}), version=version)
        )

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        session_id: str = "",
        version: str = "",
        confirmed: bool = False,
    ) -> LLMExecuteToolResponse:
        """Call a tool and wait for its result.

        A failed call, e.g. invalid arguments, a timeout or an error of the tool, is reported in the
        response (``success`` is false and ``error`` says why), so that it can be given to a model.
        ``version`` pins the version to call; by default the latest one. A tool whose behavior
        requires confirmation runs only with ``confirmed=True``, once a person approved the call.
        """
        return self.execute_tool(
            LLMExecuteToolRequest(
                tool_name=name,
                arguments_json=json.dumps(arguments or {}),
                session_id=session_id,
                version=version,
                confirmed=confirmed,
            )
        )

    def execute_async(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        session_id: str = "",
        version: str = "",
        confirmed: bool = False,
    ) -> LLMExecuteToolAsyncResponse:
        """Start a call to a tool in the background; poll :meth:`get_task` for its result."""
        return self.execute_tool_async(
            LLMExecuteToolRequest(
                tool_name=name,
                arguments_json=json.dumps(arguments or {}),
                session_id=session_id,
                version=version,
                confirmed=confirmed,
            )
        )

    def execute_tool_call(
        self,
        tool_call: LLMToolCall,
        tool_names: dict[str, str],
        *,
        session_id: str = "",
        confirmed: bool = False,
    ) -> LLMExecuteToolResponse:
        """Run the tool a model called, given the mapping returned by :meth:`build_model_tools`."""
        name = tool_names.get(tool_call.function.name)
        if name is None:
            return LLMExecuteToolResponse(success=False, error=f"unknown tool {tool_call.function.name}")
        return self.execute_tool(
            LLMExecuteToolRequest(
                tool_name=name,
                arguments_json=tool_call.function.arguments or "{}",
                session_id=session_id,
                confirmed=confirmed,
            )
        )
