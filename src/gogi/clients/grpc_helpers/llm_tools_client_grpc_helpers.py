from gogi.models.llm.llm_tool_service_definition import (
    LLMCostMetadata,
    LLMExecutionLimits,
    LLMRateLimits,
    LLMToolBehavior,
    LLMToolServiceDefinition,
)
from gogi.models.llm.requests.llm_tools.llm_discover_tools_request import LLMDiscoverToolsRequest
from gogi.models.llm.requests.llm_tools.llm_execute_tool_request import LLMExecuteToolRequest
from gogi.models.llm.requests.llm_tools.llm_get_task_request import LLMGetTaskRequest
from gogi.models.llm.requests.llm_tools.llm_register_mcp_server_request import LLMRegisterMcpServerRequest
from gogi.models.llm.requests.llm_tools.llm_register_tool_request import LLMRegisterToolRequest
from gogi.models.llm.requests.llm_tools.llm_validate_tool_request import LLMValidateToolRequest
from gogi.models.llm.responses.llm_tools.llm_discover_tools_response import LLMDiscoverToolsResponse
from gogi.models.llm.responses.llm_tools.llm_execute_tool_async_response import LLMExecuteToolAsyncResponse
from gogi.models.llm.responses.llm_tools.llm_execute_tool_response import LLMExecuteToolResponse
from gogi.models.llm.responses.llm_tools.llm_get_task_response import LLMGetTaskResponse
from gogi.models.llm.responses.llm_tools.llm_register_mcp_server_response import LLMRegisterMcpServerResponse
from gogi.models.llm.responses.llm_tools.llm_register_tool_response import LLMRegisterToolResponse
from gogi.models.llm.responses.llm_tools.llm_validate_tool_response import LLMValidateToolResponse
from gogi.v1 import cost_metadata_pb2, execution_limits_pb2, llm_tool_pb2, llm_tool_service_pb2, rate_limits_pb2


class LLMToolsClientGRPCHelper:

    @staticmethod
    def tool_behavior_to_grpc(behavior: LLMToolBehavior) -> llm_tool_pb2.ToolBehavior:
        return llm_tool_pb2.ToolBehavior(
            is_read_only=behavior.is_read_only,
            is_idempotent=behavior.is_idempotent,
            requires_confirmation=behavior.requires_confirmation,
            typical_latency_ms=behavior.typical_latency_ms,
            side_effects=behavior.side_effects,
        )

    @staticmethod
    def tool_behavior_from_grpc(behavior: llm_tool_pb2.ToolBehavior) -> LLMToolBehavior:
        return LLMToolBehavior(
            is_read_only=behavior.is_read_only,
            is_idempotent=behavior.is_idempotent,
            requires_confirmation=behavior.requires_confirmation,
            typical_latency_ms=behavior.typical_latency_ms,
            side_effects=list(behavior.side_effects),
        )

    @staticmethod
    def rate_limits_to_grpc(rate_limits: LLMRateLimits) -> rate_limits_pb2.RateLimits:
        return rate_limits_pb2.RateLimits(
            requests_per_minute=rate_limits.requests_per_minute,
            requests_per_session=rate_limits.requests_per_session,
            daily_limit=rate_limits.daily_limit,
        )

    @staticmethod
    def rate_limits_from_grpc(rate_limits: rate_limits_pb2.RateLimits) -> LLMRateLimits:
        return LLMRateLimits(
            requests_per_minute=rate_limits.requests_per_minute,
            requests_per_session=rate_limits.requests_per_session,
            daily_limit=rate_limits.daily_limit,
        )

    @staticmethod
    def cost_metadata_to_grpc(cost: LLMCostMetadata) -> cost_metadata_pb2.CostMetadata:
        return cost_metadata_pb2.CostMetadata(
            estimated_cost_usd=cost.estimated_cost_usd,
            billing_category=cost.billing_category,
        )

    @staticmethod
    def cost_metadata_from_grpc(cost: cost_metadata_pb2.CostMetadata) -> LLMCostMetadata:
        return LLMCostMetadata(
            estimated_cost_usd=cost.estimated_cost_usd,
            billing_category=cost.billing_category,
        )

    @staticmethod
    def execution_limits_to_grpc(limits: LLMExecutionLimits) -> execution_limits_pb2.ExecutionLimits:
        return execution_limits_pb2.ExecutionLimits(
            timeout_seconds=limits.timeout_seconds,
            memory_limit_mb=limits.memory_limit_mb,
            cpu_limit_millicores=limits.cpu_limit_millicores,
            max_response_size_kb=limits.max_response_size_kb,
            max_retries=limits.max_retries,
        )

    @staticmethod
    def execution_limits_from_grpc(limits: execution_limits_pb2.ExecutionLimits) -> LLMExecutionLimits:
        return LLMExecutionLimits(
            timeout_seconds=limits.timeout_seconds,
            memory_limit_mb=limits.memory_limit_mb,
            cpu_limit_millicores=limits.cpu_limit_millicores,
            max_response_size_kb=limits.max_response_size_kb,
            max_retries=limits.max_retries,
        )

    @staticmethod
    def tool_definition_to_grpc(tool: LLMToolServiceDefinition) -> llm_tool_pb2.ToolServiceDefinition:
        return llm_tool_pb2.ToolServiceDefinition(
            name=tool.name,
            version=tool.version,
            owner=tool.owner,
            description=tool.description,
            parameters_json=tool.parameters_json,
            returns_json=tool.returns_json,
            behavior=LLMToolsClientGRPCHelper.tool_behavior_to_grpc(tool.behavior) if tool.behavior else None,
            rate_limits=LLMToolsClientGRPCHelper.rate_limits_to_grpc(tool.rate_limits) if tool.rate_limits else None,
            cost=LLMToolsClientGRPCHelper.cost_metadata_to_grpc(tool.cost) if tool.cost else None,
            required_permissions=tool.required_permissions,
            capabilities=tool.capabilities,
            tags=tool.tags,
            endpoint=tool.endpoint,
            credential_ref=tool.credential_ref,
            execution_limits=LLMToolsClientGRPCHelper.execution_limits_to_grpc(tool.execution_limits) if tool.execution_limits else None,
            mcp_server_url=tool.mcp_server_url,
        )

    @staticmethod
    def tool_definition_from_grpc(tool: llm_tool_pb2.ToolServiceDefinition) -> LLMToolServiceDefinition:
        return LLMToolServiceDefinition(
            name=tool.name,
            version=tool.version,
            owner=tool.owner,
            description=tool.description,
            parameters_json=tool.parameters_json,
            returns_json=tool.returns_json,
            behavior=LLMToolsClientGRPCHelper.tool_behavior_from_grpc(tool.behavior) if tool.HasField("behavior") else None,
            rate_limits=LLMToolsClientGRPCHelper.rate_limits_from_grpc(tool.rate_limits) if tool.HasField("rate_limits") else None,
            cost=LLMToolsClientGRPCHelper.cost_metadata_from_grpc(tool.cost) if tool.HasField("cost") else None,
            required_permissions=list(tool.required_permissions),
            capabilities=list(tool.capabilities),
            tags=list(tool.tags),
            endpoint=tool.endpoint,
            credential_ref=tool.credential_ref,
            execution_limits=LLMToolsClientGRPCHelper.execution_limits_from_grpc(tool.execution_limits) if tool.HasField("execution_limits") else None,
            mcp_server_url=tool.mcp_server_url,
        )

    # --- RegisterTool ---

    @staticmethod
    def build_grpc_register_tool_request(request: LLMRegisterToolRequest) -> llm_tool_service_pb2.RegisterToolRequest:
        return llm_tool_service_pb2.RegisterToolRequest(
            tool=LLMToolsClientGRPCHelper.tool_definition_to_grpc(request.tool),
        )

    @staticmethod
    def serialize_register_tool_grpc_response(grpc_response: llm_tool_service_pb2.RegisterToolResponse) -> LLMRegisterToolResponse:
        return LLMRegisterToolResponse(
            name=grpc_response.name,
            version=grpc_response.version,
            status=grpc_response.status,
        )

    # --- DiscoverTools ---

    @staticmethod
    def build_grpc_discover_tools_request(request: LLMDiscoverToolsRequest) -> llm_tool_service_pb2.DiscoverToolsRequest:
        return llm_tool_service_pb2.DiscoverToolsRequest(
            namespace=request.namespace,
            capabilities=request.capabilities,
            tags=request.tags,
            read_only=request.read_only,
            version_constraint=request.version_constraint,
        )

    @staticmethod
    def serialize_discover_tools_grpc_response(grpc_response: llm_tool_service_pb2.DiscoverToolsResponse) -> LLMDiscoverToolsResponse:
        return LLMDiscoverToolsResponse(
            tools=[LLMToolsClientGRPCHelper.tool_definition_from_grpc(tool) for tool in grpc_response.tools],
            relevance_scores=dict(grpc_response.relevance_scores),
        )

    # --- ExecuteTool ---

    @staticmethod
    def build_grpc_execute_tool_request(request: LLMExecuteToolRequest) -> llm_tool_service_pb2.ExecuteToolRequest:
        return llm_tool_service_pb2.ExecuteToolRequest(
            tool_name=request.tool_name,
            arguments_json=request.arguments_json,
            session_id=request.session_id,
        )

    @staticmethod
    def serialize_execute_tool_grpc_response(grpc_response: llm_tool_service_pb2.ExecuteToolResponse) -> LLMExecuteToolResponse:
        return LLMExecuteToolResponse(
            success=grpc_response.success,
            result_json=grpc_response.result_json,
            error=grpc_response.error,
            execution_time_ms=grpc_response.execution_time_ms,
        )

    # --- ValidateTool ---

    @staticmethod
    def build_grpc_validate_tool_request(request: LLMValidateToolRequest) -> llm_tool_service_pb2.ValidateToolRequest:
        return llm_tool_service_pb2.ValidateToolRequest(
            tool_name=request.tool_name,
            arguments_json=request.arguments_json,
        )

    @staticmethod
    def serialize_validate_tool_grpc_response(grpc_response: llm_tool_service_pb2.ValidateToolResponse) -> LLMValidateToolResponse:
        return LLMValidateToolResponse(
            valid=grpc_response.valid,
            errors=list(grpc_response.errors),
        )

    # --- ExecuteToolAsync / GetTask ---

    @staticmethod
    def build_grpc_execute_tool_async_request(request: LLMExecuteToolRequest) -> llm_tool_service_pb2.ExecuteToolRequest:
        return LLMToolsClientGRPCHelper.build_grpc_execute_tool_request(request)

    @staticmethod
    def serialize_execute_tool_async_grpc_response(grpc_response: llm_tool_service_pb2.ExecuteToolAsyncResponse) -> LLMExecuteToolAsyncResponse:
        return LLMExecuteToolAsyncResponse(
            task_id=grpc_response.task_id,
            status=grpc_response.status,
        )

    @staticmethod
    def build_grpc_get_task_request(request: LLMGetTaskRequest) -> llm_tool_service_pb2.GetTaskRequest:
        return llm_tool_service_pb2.GetTaskRequest(task_id=request.task_id)

    @staticmethod
    def serialize_get_task_grpc_response(grpc_response: llm_tool_service_pb2.GetTaskResponse) -> LLMGetTaskResponse:
        return LLMGetTaskResponse(
            task_id=grpc_response.task_id,
            status=grpc_response.status,
            result_json=grpc_response.result_json,
            error=grpc_response.error,
        )

    # --- RegisterMcpServer ---

    @staticmethod
    def build_grpc_register_mcp_server_request(request: LLMRegisterMcpServerRequest) -> llm_tool_service_pb2.RegisterMcpServerRequest:
        return llm_tool_service_pb2.RegisterMcpServerRequest(
            server_url=request.server_url,
            namespace=request.namespace,
            credential_ref=request.credential_ref,
            policy_overrides=LLMToolsClientGRPCHelper.tool_behavior_to_grpc(request.policy_overrides) if request.policy_overrides else None,
            rate_limit_overrides=LLMToolsClientGRPCHelper.rate_limits_to_grpc(request.rate_limit_overrides) if request.rate_limit_overrides else None,
        )

    @staticmethod
    def serialize_register_mcp_server_grpc_response(grpc_response: llm_tool_service_pb2.RegisterMcpServerResponse) -> LLMRegisterMcpServerResponse:
        return LLMRegisterMcpServerResponse(
            imported_tool_names=list(grpc_response.imported_tool_names),
        )
