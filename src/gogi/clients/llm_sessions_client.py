
from typing import Optional

from gogi.clients.models.llm.llm_session import LLMSession
from gogi.v1 import llm_session_service_pb2_grpc
from gogi.clients.base_client import BaseClient

from gogi.clients.grpc_helpers.llm_sessions_client_grpc_helpers import LLMSessionsClientGRPCHelper
from gogi.clients.models.llm.requests.create_llm_session_request import CreateSessionRequest

class LLMSessionMemoryManager(BaseClient):
    
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-sessions", logger=logger)
        self._grpc_helper = LLMSessionsClientGRPCHelper()
        self._stub = llm_session_service_pb2_grpc.LLMSessionServerStub(self._channel)

    def save_memory(request: SaveLLMSessionMemoryRequest) -> SaveLLMSessionMemoryResponse:
        pass 
    def get_memory(request: GetLLMSessionMemoryRequest) -> GetLLMSessionMemoryResponse:
        pass 

    def delete_memory(request: DeleteLLMSessionMemoryRequest) -> DeleteLLMSessionMemoryResponse:
        pass 

    def clear_user_memory(request: ClearUserLLMSessionMemoryRequest) -> ClearUserLLMSessionMemoryResponse:
        pass

class LLMSessionsClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-sessions", logger=logger)
        self._grpc_helper = LLMSessionsClientGRPCHelper()
        self._stub = llm_session_service_pb2_grpc.LLMSessionServerStub(self._channel)
        self._memory_manager = LLMSessionMemoryManager(platform=platform, logger=logger)

    def get_or_create_session(self, request: CreateSessionRequest) -> LLMSession:
        pass 

    def delete_session(self, request: DeleteLLMSessionRequest) -> DeleteLLMSessionResponse:
        pass

    def list_sessions(self, request: ListLLMSessionsRequest) -> ListLLMSessionsResponse:
        pass 

    def add_messages_to_session(self, request: AddMessagesToLLMSessionRequest) -> AddMMessagesToLLMSessionResponse:
        pass 

    def get_messages(self, request: GetMessagesFromLLMSessionRequest) -> GetMessagesFromLLMSessionResponse:
        pass 

    def save_memory(self, request: SaveLLMSessionMemoryRequest) -> SaveLLMSessionMemoryResponse:
        return self._memory_manager.save_memory(request=request) 
    
    def get_memory(self, request: GetLLMSessionMemoryRequest) -> GetLLMSessionMemoryResponse:
        return self._memory_manager.get_memory(request=request) 

    def delete_memory(self, request: DeleteLLMSessionMemoryRequest) -> DeleteLLMSessionMemoryResponse:
        return self._memory_manager.delete_memory(request=request) 

    def clear_user_memory(self, request: ClearUserLLMSessionMemoryRequest) -> ClearUserLLMSessionMemoryResponse:
        return self._memory_manager.clear_user_memory(request=request)


        