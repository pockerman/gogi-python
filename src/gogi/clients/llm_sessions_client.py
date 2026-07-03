
from typing import Optional

from gogi.models.llm.llm_session import LLMSession
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import AddMessagesToLLMSessionRequest
from gogi.models.llm.requests.llm_session.clear_user_llm_session_memory_request import ClearUserLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_memory_request import DeleteLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_request import DeleteLLMSessionRequest
from gogi.models.llm.requests.llm_session.get_llm_session_memory_request import GetLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.get_messages_from_llm_session_request import GetMessagesFromLLMSessionRequest
from gogi.models.llm.requests.llm_session.list_llm_session_request import ListLLMSessionsRequest
from gogi.models.llm.requests.llm_session.save_llm_session_memory_request import SaveLLMSessionMemoryRequest
from gogi.models.llm.responses.llm_session.add_messages_to_llm_session_response import AddMMessagesToLLMSessionResponse
from gogi.models.llm.responses.llm_session.clear_user_llm_session_memory_response import ClearUserLLMSessionMemoryResponse
from gogi.models.llm.responses.llm_session.delete_llm_session_memory_response import DeleteLLMSessionMemoryResponse
from gogi.models.llm.responses.llm_session.delete_llm_session_response import DeleteLLMSessionResponse
from gogi.models.llm.responses.llm_session.get_llm_session_memory_response import GetLLMSessionMemoryResponse
from gogi.models.llm.responses.llm_session.get_messages_from_llm_session_response import GetMessagesFromLLMSessionResponse
from gogi.models.llm.responses.llm_session.list_llm_sessions_response import ListLLMSessionsResponse
from gogi.models.llm.responses.llm_session.save_llm_session_memory_response import SaveLLMSessionMemoryResponse
from gogi.v1 import llm_session_service_pb2_grpc
from gogi.clients.base_client import BaseClient

from gogi.clients.grpc_helpers.llm_sessions_client_grpc_helpers import LLMSessionsClientGRPCHelper
from gogi.models.llm.requests.llm_session.create_llm_session_request import CreateLLMSessionRequest

class LLMSessionMemoryManager(BaseClient):
    
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-sessions", logger=logger)
        self._grpc_helper = LLMSessionsClientGRPCHelper()
        self._stub = llm_session_service_pb2_grpc.LLMSessionServerStub(self._channel)

    def save_memory(self, request: SaveLLMSessionMemoryRequest) -> SaveLLMSessionMemoryResponse:
        grpc_request = self._grpc_helper.build_grpc_save_memory_request(request)
        grpc_response = self._stub.SaveMemory(grpc_request)
        response = self._grpc_helper.serialize_save_memory_grpc_response(grpc_response)
        return response  
    
    def get_memory(self, request: GetLLMSessionMemoryRequest) -> GetLLMSessionMemoryResponse:
        grpc_request = self._grpc_helper.build_grpc_get_memory_request(request)
        grpc_response = self._stub.GetMemory(grpc_request)
        response = self._grpc_helper.serialize_get_memory_grpc_response(grpc_response)
        return response   

    def delete_memory(self, request: DeleteLLMSessionMemoryRequest) -> DeleteLLMSessionMemoryResponse:
        grpc_request = self._grpc_helper.build_grpc_delete_memory_request(request)
        grpc_response = self._stub.DeleteMemory(grpc_request)
        response = self._grpc_helper.serialize_delete_memory_grpc_response(grpc_response)
        return response 

    def clear_user_memory(self, request: ClearUserLLMSessionMemoryRequest) -> ClearUserLLMSessionMemoryResponse:
        grpc_request = self._grpc_helper.build_grpc_clear_user_memory_request(request)
        grpc_response = self._stub.ClearUserMemory(grpc_request)
        response = self._grpc_helper.serialize_clear_user_memory_grpc_response(grpc_response)
        return response

class LLMSessionsClient(BaseClient):
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llm-sessions", logger=logger)
        self._grpc_helper = LLMSessionsClientGRPCHelper()
        self._stub = llm_session_service_pb2_grpc.LLMSessionServerStub(self._channel)
        self._memory_manager = LLMSessionMemoryManager(platform=platform, logger=logger)

    def get_or_create_session(self, request: CreateLLMSessionRequest) -> LLMSession:
        grpc_request = self._grpc_helper.build_grpc_create_session_request(request)
        grpc_response = self._stub.GetOrCreateSession(grpc_request)
        response = self._grpc_helper.serialize_create_session_grpc_response(grpc_response)
        return response

    def delete_session(self, request: DeleteLLMSessionRequest) -> DeleteLLMSessionResponse:
        grpc_request = self._grpc_helper.build_grpc_delete_session_request(request)
        grpc_response = self._stub.DeleteSession(grpc_request)
        response = self._grpc_helper.serialize_delete_session_grpc_response(grpc_response)
        return response

    def list_sessions(self, request: ListLLMSessionsRequest) -> ListLLMSessionsResponse:
        grpc_request = self._grpc_helper.build_grpc_list_sessions_request(request)
        grpc_response = self._stub.ListSessions(grpc_request)
        response = self._grpc_helper.serialize_list_sessions_grpc_response(grpc_response)
        return response  

    def add_messages_to_session(self, request: AddMessagesToLLMSessionRequest) -> AddMMessagesToLLMSessionResponse:
        grpc_request = self._grpc_helper.build_grpc_add_messages_to_session_request(request)
        grpc_response = self._stub.AddMessages(grpc_request)
        response = self._grpc_helper.serialize_add_messages_to_session_grpc_response(grpc_response)
        return response 

    def get_messages(self, request: GetMessagesFromLLMSessionRequest) -> GetMessagesFromLLMSessionResponse:
        grpc_request = self._grpc_helper.build_grpc_get_messages_request(request)
        grpc_response = self._stub.GetMessages(grpc_request)
        response = self._grpc_helper.serialize_get_messages_grpc_response(grpc_response)
        return response 

    def save_memory(self, request: SaveLLMSessionMemoryRequest) -> SaveLLMSessionMemoryResponse:
        return self._memory_manager.save_memory(request=request) 
    
    def get_memory(self, request: GetLLMSessionMemoryRequest) -> GetLLMSessionMemoryResponse:
        return self._memory_manager.get_memory(request=request) 

    def delete_memory(self, request: DeleteLLMSessionMemoryRequest) -> DeleteLLMSessionMemoryResponse:
        return self._memory_manager.delete_memory(request=request) 

    def clear_user_memory(self, request: ClearUserLLMSessionMemoryRequest) -> ClearUserLLMSessionMemoryResponse:
        return self._memory_manager.clear_user_memory(request=request)


        