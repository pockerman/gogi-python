
from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import AddMessagesToLLMSessionRequest
from gogi.models.llm.requests.llm_session.clear_user_llm_session_memory_request import ClearUserLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_memory_request import DeleteLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_request import DeleteLLMSessionRequest
from gogi.models.llm.responses.llm_session.add_messages_to_llm_session_response import AddMMessagesToLLMSessionResponse
from gogi.models.llm.responses.llm_session.clear_user_llm_session_memory_response import ClearUserLLMSessionMemoryResponse
from gogi.models.llm.responses.llm_session.delete_llm_session_memory_response import DeleteLLMSessionMemoryResponse
from gogi.models.llm.responses.llm_session.delete_llm_session_response import DeleteLLMSessionResponse
from gogi.v1 import llm_session_service_pb2, llm_message_pb2, llm_tool_pb2

from gogi.models.llm.llm_session import LLMSession
from gogi.models.llm.requests.llm_session.create_llm_session_request import CreateLLMSessionRequest

class LLMSessionsClientGRPCHelper:


    @staticmethod
    def build_grpc_create_session_request(request: CreateLLMSessionRequest) -> llm_session_service_pb2.GetOrCreateSessionRequest:
        return llm_session_service_pb2.GetOrCreateSessionRequest(user_id=request.user_id, session_id=request.session_id)
    
    @staticmethod
    def serialize_create_session_grpc_response(grpc_response: llm_session_service_pb2.GetOrCreateSessionRequest) -> LLMSession:
        return LLMSession(session_id=grpc_response.session.session_id, 
                          user_id=grpc_response.session.user_id,
                          created_at=grpc_response.session.created_at, 
                          updated_at=grpc_response.session.updated_at)
    
    @staticmethod
    def llm_message_to_grpc(msg: LLMMessage) -> llm_message_pb2.LLMMessage:
        return llm_message_pb2.LLMMessage(
            role=msg.role,
            content=msg.content or "",
            tool_calls=[
                llm_tool_pb2.ToolCall(
                    id=tc.id,
                    type=tc.type,
                    function=llm_tool_pb2.ToolCallFunction(
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                    ),
                )
                for tc in msg.tool_calls
            ],
            tool_call_id=msg.tool_call_id or "",
            name=msg.name or "",
            timestamp=msg.timestamp,
        )
        

    @staticmethod
    def build_grpc_add_messages_to_session_request(request: AddMessagesToLLMSessionRequest) -> llm_session_service_pb2.AddMessagesRequest:
        return llm_session_service_pb2.AddMessagesRequest(session_id=request.session_id,
                                                          messages=[
                                                                LLMSessionsClientGRPCHelper.llm_message_to_grpc(m)
                                                                for m in request.messages
                                                            ],
    )
    
    @staticmethod
    def serialize_add_messages_to_session_grpc_response(grpc_response: llm_session_service_pb2.AddMessagesResponse) -> AddMMessagesToLLMSessionResponse:
        print(grpc_response)
        return AddMMessagesToLLMSessionResponse(success=grpc_response.success, message_count=grpc_response.message_count) 
    
         
    @staticmethod
    def build_grpc_delete_session_request(request: DeleteLLMSessionRequest) -> llm_session_service_pb2.DeleteSessionRequest:
        return llm_session_service_pb2.DeleteSessionRequest(session_id=request.session_id)

    @staticmethod
    def serialize_delete_session_grpc_response(grpc_response: llm_session_service_pb2.DeleteSessionResponse) -> DeleteLLMSessionResponse:
        return DeleteLLMSessionResponse(success=grpc_response.success)

    @staticmethod
    def build_grpc_delete_memory_request(request: DeleteLLMSessionMemoryRequest) -> llm_session_service_pb2.DeleteMemoryRequest:
        return llm_session_service_pb2.DeleteMemoryRequest(session_id=request.session_id, user_id=request.user_id, key=request.key)
       
    @staticmethod
    def serialize_delete_memory_grpc_response(grpc_response: llm_session_service_pb2.DeleteSessionResponse) -> DeleteLLMSessionMemoryResponse:
        return DeleteLLMSessionMemoryResponse(success=grpc_response.success) 
    

    @staticmethod
    def build_grpc_clear_user_memory_request(request: ClearUserLLMSessionMemoryRequest) -> llm_session_service_pb2.ClearUserMemoryRequest:
        return llm_session_service_pb2.ClearUserMemoryRequest(user_id=request.user_id)
    
    @staticmethod
    def serialize_clear_user_memory_grpc_response(grpc_response: llm_session_service_pb2.ClearUserMemoryResponse) -> ClearUserLLMSessionMemoryResponse:
        return ClearUserLLMSessionMemoryResponse(count=grpc_response.count)