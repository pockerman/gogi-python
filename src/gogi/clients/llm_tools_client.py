from gogi.models.llm.requests.llm_tools.llm_discover_tools_request import LLMDiscoverToolsRequest
from gogi.models.llm.requests.llm_tools.llm_execute_tool_request import LLMExecuteToolRequest
from gogi.models.llm.requests.llm_tools.llm_register_tool_request import LLMRegisterToolRequest
from gogi.models.llm.responses.llm_tools.llm_discover_tools_response import LLMDiscoverToolsResponse
from gogi.models.llm.responses.llm_tools.llm_execute_tool_response import LLMExecuteToolResponse
from gogi.models.llm.responses.llm_tools.llm_register_tool_response import LLMRegisterToolResponse
from gogi.v1 import llm_tool_pb2_grpc
from gogi.clients.base_client import BaseClient
from gogi.clients.grpc_helpers.llm_tools_client_grpc_helpers import LLMToolsClientGRPCHelper


class LLMToolsClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-tools", logger=logger)
        self._grpc_helper = LLMToolsClientGRPCHelper()
        self._stub = llm_tool_pb2_grpc.LLMToolServerStub(self._channel)

    def register_tool(self, request: LLMRegisterToolRequest) -> LLMRegisterToolResponse:
        pass

    def discover_tools(self, request: LLMDiscoverToolsRequest) ->  LLMDiscoverToolsResponse:
        pass

    def execute_tool(self, request: LLMExecuteToolRequest ) -> LLMExecuteToolResponse:
        pass
        