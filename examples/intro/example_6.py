"""This example illustrates the LLMToolsClient in gogi.
The client allows users to:

- Register a new tool with the tool registry
- Discover tools by namespace, capability or tag
- Validate arguments against a tool's schema before calling it
- Execute a tool synchronously
- Execute a long-running tool asynchronously and poll for its result
- Register an external MCP server so its tools are imported into the registry


"""

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
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

if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # register a new tool with the registry
    tool = LLMToolServiceDefinition(
        name="get_weather",
        version="1.0.0",
        owner="123",
        description="Get the current weather for a given city.",
        parameters_json='{"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}',
        returns_json='{"type": "object", "properties": {"temperature_c": {"type": "number"}}}',
        behavior=LLMToolBehavior(is_read_only=True, is_idempotent=True, typical_latency_ms=250),
        rate_limits=LLMRateLimits(requests_per_minute=60, requests_per_session=200, daily_limit=1000),
        cost=LLMCostMetadata(estimated_cost_usd=0.0, billing_category="free"),
        capabilities=["weather.read"],
        tags=["weather", "external-api"],
        endpoint="https://weather.example.com/api/v1/current",
        execution_limits=LLMExecutionLimits(timeout_seconds=10, max_retries=2),
    )
    register_tool_response = platform.tools.register_tool(request=LLMRegisterToolRequest(tool=tool))
    rich_print(f"Register tool response {register_tool_response}")

    # discover tools by capability
    discover_tools_response = platform.tools.discover_tools(
        request=LLMDiscoverToolsRequest(capabilities=["weather.read"], read_only=True)
    )
    rich_print(f"Discover tools response {discover_tools_response}")

    # validate arguments before calling the tool
    validate_tool_response = platform.tools.validate_tool(
        request=LLMValidateToolRequest(tool_name="get_weather", arguments_json='{"city": "London"}')
    )
    rich_print(f"Validate tool response {validate_tool_response}")

    # execute the tool synchronously
    execute_tool_response = platform.tools.execute_tool(
        request=LLMExecuteToolRequest(tool_name="get_weather", arguments_json='{"city": "London"}', session_id="123")
    )
    rich_print(f"Execute tool response {execute_tool_response}")

    # execute a long-running tool asynchronously and poll for its result
    execute_tool_async_response = platform.tools.execute_tool_async(
        request=LLMExecuteToolRequest(tool_name="get_weather", arguments_json='{"city": "London"}', session_id="123")
    )
    rich_print(f"Execute tool async response {execute_tool_async_response}")

    get_task_response = platform.tools.get_task(request=LLMGetTaskRequest(task_id=execute_tool_async_response.task_id))
    rich_print(f"Get task response {get_task_response}")

    # register an external MCP server; its tools are imported into the registry
    # under the given namespace
    register_mcp_server_response = platform.tools.register_mcp_server(
        request=LLMRegisterMcpServerRequest(
            server_url="https://mcp.example.com",
            namespace="123",
            policy_overrides=LLMToolBehavior(requires_confirmation=True),
            rate_limit_overrides=LLMRateLimits(requests_per_minute=30),
        )
    )
    rich_print(f"Register MCP server response {register_mcp_server_response}")
