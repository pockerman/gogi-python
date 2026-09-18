from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.llm_tools_client_grpc_helpers import (
    LLMToolsClientGRPCHelper,
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

    def get_task(self, request: LLMGetTaskRequest) -> LLMGetTaskResponse:
        grpc_request = self._grpc_helper.build_grpc_get_task_request(request)
        grpc_response = self._stub.GetTask(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_get_task_grpc_response(grpc_response)

    def register_mcp_server(self, request: LLMRegisterMcpServerRequest) -> LLMRegisterMcpServerResponse:
        grpc_request = self._grpc_helper.build_grpc_register_mcp_server_request(request)
        grpc_response = self._stub.RegisterMcpServer(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_register_mcp_server_grpc_response(grpc_response)
