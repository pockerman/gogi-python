
from gogi.v1 import llm_session_service_pb2

from gogi.models.llm.llm_session import LLMSession
from gogi.models.llm.requests.llm_session.create_llm_session_request import CreateSessionRequest

class LLMSessionsClientGRPCHelper:
    
    @staticmethod
    def build_grpc_create_session_request(request: CreateSessionRequest) -> llm_session_service_pb2.GetOrCreateSessionRequest:
        return llm_session_service_pb2.GetOrCreateSessionRequest(user_id=request.user_id, session_id=request.session_id)
    
    @staticmethod
    def serialize_create_session_grpc_response(grpc_response: llm_session_service_pb2.GetOrCreateSessionRequest) -> LLMSession:
        return LLMSession(session_id=grpc_response.session_id, user_id=grpc_response.user_id,
                          created_at=grpc_response.created_at, updated_at=grpc_response.updated_at)