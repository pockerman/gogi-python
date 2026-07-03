from datetime import datetime, UTC

from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.llm_tool_definition import LLMToolCall, ToolCallFunction
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
    
     
        
    @staticmethod
    def build_grpc_get_messages_request(request: GetMessagesFromLLMSessionRequest) -> llm_session_service_pb2.GetMessagesRequest:
        return llm_session_service_pb2.GetMessagesRequest(session_id=request.session_id,
                                                          limit=request.limit,
                                                          offset=request.offset,
                                                          strategy=request.strategy)
        
    @staticmethod   
    def serialize_get_messages_grpc_response(grpc_response: llm_session_service_pb2.GetMessagesResponse) -> GetMessagesFromLLMSessionResponse:

        messages = []
        for msg in grpc_response.messages:
            tool_calls = [
                LLMToolCall(
                    id=tc.id,
                    type=tc.type,
                    function=ToolCallFunction(
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                    ),
                )
                for tc in msg.tool_calls
            ]

            messages.append(
                LLMMessage(
                    role=msg.role,
                    content=msg.content if msg.HasField("content") else None,
                    tool_calls=tool_calls,
                    tool_call_id=msg.tool_call_id if msg.HasField("tool_call_id") else None,
                    name=msg.name if msg.HasField("name") else None,
                    timestamp=msg.timestamp,
                )
            )

        return GetMessagesFromLLMSessionResponse(
            messages=messages,
            total_count=grpc_response.total_count,
        )

     
    @staticmethod
    def build_grpc_list_sessions_request(request: ListLLMSessionsRequest) -> llm_session_service_pb2.ListSessionsRequest:
        return llm_session_service_pb2.ListSessionsRequest(user_id=request.user_id)
        
   
    @staticmethod
    def serialize_list_sessions_grpc_response(
        grpc_response: llm_session_service_pb2.ListSessionsResponse,
    ) -> ListLLMSessionsResponse:

        sessions = [
            LLMSession(
                session_id=session.session_id,
                user_id=session.user_id,
                created_at=datetime.fromtimestamp(session.created_at, tz=UTC),
                updated_at=datetime.fromtimestamp(session.updated_at, tz=UTC),
            )
            for session in grpc_response.sessions
        ]

        return ListLLMSessionsResponse(sessions=sessions)
    
    @staticmethod
    def build_grpc_save_memory_request(
    request: SaveLLMSessionMemoryRequest,
    ) -> llm_session_service_pb2.SaveMemoryRequest:
        return llm_session_service_pb2.SaveMemoryRequest(
            user_id=request.user_id,
            key=request.key,
            value=request.value,
            session_id=request.session_id,
        )
    
    @staticmethod
    def serialize_save_memory_grpc_response(grpc_response: llm_session_service_pb2.SaveMemoryResponse,) -> SaveLLMSessionMemoryResponse:
        return SaveLLMSessionMemoryResponse(
            success=grpc_response.success,
        )

    @staticmethod
    def build_grpc_get_memory_request(request: GetLLMSessionMemoryRequest,) -> llm_session_service_pb2.GetMemoryRequest:
        return llm_session_service_pb2.GetMemoryRequest(
            session_id=request.session_id,
            user_id=request.user_id,
            key=request.key
        )

    @staticmethod
    def serialize_get_memory_grpc_response(grpc_response: llm_session_service_pb2.GetMemoryResponse,) -> GetLLMSessionMemoryResponse:
        return GetLLMSessionMemoryResponse(
            memories=dict(grpc_response.memories),
        )