
from typing import Optional, List, Any 

from gogi.clients.models.llm.llm_capabilities import LLMCapabilities
from gogi.clients.models.llm.requests.llm_register_request import LLMRegisterRequest
from gogi.clients.models.llm.requests.llm_request_status import GetLLMStatusRequest
from gogi.clients.models.llm.requests.llm_run_request import LLMRunRequest
from gogi.clients.models.llm.requests.list_registered_llm_request import ListRegisteredLLMsRequest
from gogi.clients.models.llm.responses.llm_run_response import LLMRunResponse
from gogi.clients.models.llm.responses.llm_register_response import LLMRegisterResponse
from gogi.clients.models.llm.responses.list_registered_llms_response import ListRegisteredLLMsResponse

from gogi.clients.models.llm.llm_message import LLMessage
from gogi.clients.models.llm.llm_tool_definition import LLMToolCall, LLMToolDefinition, ToolCallFunction
from gogi.clients.models.llm.llm_run_request_config import LLMRunRequestConfig
from gogi.clients.models.llm.llm_token_usage import LLMTokenUsage
from gogi.clients.models.llm.registered_llm import RegisteredLLM
from gogi.clients.models.llm.llm_model_info import LLMModelInfo


from gogi.clients.models.llm.responses.llm_status_response import LLMStatusResponse
from gogi.v1 import llm_model_service_pb2, llm_model_service_pb2_grpc



class LLMModelsClientGRPCHelper:

    @staticmethod
    def validate_provider_in_request(request: LLMRunRequest, providers: list[str]) -> None:
        if request.config.provider not in providers:
            raise ValueError(f"Provider={request.config.provider} not in {providers}")
        
    @staticmethod
    def validate_provider_supports_model(request: LLMRunRequest, models: Optional[list[str]]) -> None:
        if models is None:
            raise ValueError(f"Provider={request.config.provider} does not support model {request.config.model}")
        
        if request.config.model not in models:
            raise ValueError(f"Provider={request.config.provider} does not support model {request.config.model}")
          
    @staticmethod
    def request_messages_to_grpc_messages(messages: List[LLMessage]) -> List[llm_model_service_pb2.LLMMessage]:
        return [llm_model_service_pb2.LLMMessage(role=msg.role, content=msg.content) for msg in messages]
    
    @staticmethod
    def request_config_to_grpc_request_config(config: LLMRunRequestConfig) -> llm_model_service_pb2.LLMRunRequestConfig:
        return llm_model_service_pb2.LLMRunRequestConfig(model=config.model, provider=config.provider,
                                                         temperature=config.temperature, max_tokens=config.max_tokens,
                                                         stop_sequences=config.stop_sequences,
                                                         frequency_penalty=config.frequency_penalty,
                                                         presence_penalty=config.presence_penalty,
                                                         system_prompt_name=config.system_prompt_name)
    
    @staticmethod
    def request_tools_to_grpcs_tools(tools: List[LLMToolDefinition]) -> List[llm_model_service_pb2.ToolDefinition]:
        return [llm_model_service_pb2.ToolDefinition(type=tool.tool_type, function=tool.function) for tool in tools] if tools else []
    
    @staticmethod
    def build_grpc_request(req: LLMRunRequest) -> llm_model_service_pb2.LLMRunRequest:
        messages = LLMModelsClientGRPCHelper.request_messages_to_grpc_messages(messages=req.messages)
        config = LLMModelsClientGRPCHelper.request_config_to_grpc_request_config(config=req.config)
        tools = LLMModelsClientGRPCHelper.request_tools_to_grpcs_tools(tools=req.tools)
        response_format = llm_model_service_pb2.ResponseFormat(type=req.response_format.response_type, 
                                                               schema_json=req.response_format.response_schema_json) if req.response_format else None

        return llm_model_service_pb2.LLMRunRequest(messages=messages, config=config,
                                                   tools=tools, response_format=response_format)
    
    @staticmethod
    def build_grpc_capabilities(request: LLMRegisterRequest) -> llm_model_service_pb2.LLMCapabilities:
        return  llm_model_service_pb2.LLMCapabilities(context_window=request.info.capabilities.context_window,
                                                      supports_vision=request.info.capabilities.supports_vision,
                                                      supports_tools=request.info.capabilities.supports_tools,
                                                      supports_streaming=request.info.capabilities.supports_streaming,
                                                      supports_json_mode=request.info.capabilities.supports_json_mode)
    
    @staticmethod
    def build_grpc_registration_request(request: LLMRegisterRequest) -> llm_model_service_pb2.RegisterLLMRequest:
        return llm_model_service_pb2.RegisterLLMRequest(info=llm_model_service_pb2.ModelInfo(name=request.info.name,
                                                                                             provider=request.info.provider,
                                                                                             capabilities=LLMModelsClientGRPCHelper.build_grpc_capabilities(request)),
                                                        endpoint=request.endpoint,
                                                        health_check=request.health_check,
                                                        adapter_type=request.adapter_type
                                                        )
    
    @staticmethod
    def grpc_token_usage_to_token_usage(grpc_usage: Optional[Any]) -> LLMTokenUsage:

        if not grpc_usage:
            return LLMTokenUsage()
        
        return LLMTokenUsage(prompt_tokens=grpc_usage.prompt_tokens, 
                             completion_tokens=grpc_usage.completion_tokens,
                             total_tokens=grpc_usage.total_tokens)
    
    @staticmethod
    def grpc_tool_calls_to_tool_call(grpc_tool_calls: list[Any]) -> List[LLMToolCall]:
        if not grpc_tool_calls:
            return []
        return [LLMToolCall(idx=tool.id, tool_type=tool.type, 
                            function=ToolCallFunction(name=tool.function.name, arguments=tool.function.arguments)) for tool in grpc_tool_calls]
    
    @staticmethod
    def list_registered_llms_request_to_grpc(request: ListRegisteredLLMsRequest) -> llm_model_service_pb2.ListRegisteredLLMsRequest:
        return llm_model_service_pb2.ListRegisteredLLMsRequest()
    
    @staticmethod
    def serialize_grpc_llm_capabilities(capabilities: llm_model_service_pb2.LLMCapabilities) -> LLMCapabilities:
        return LLMCapabilities(context_window=capabilities.context_window,
                               supports_vision=capabilities.supports_vision,
                               supports_tools=capabilities.supports_tools,
                               supports_streaming=capabilities.supports_streaming,
                               supports_json_mode=capabilities.supports_json_mode)

    @staticmethod
    def serialize_grpc_model_info(model_info: llm_model_service_pb2.ModelInfo) -> LLMModelInfo:
        return LLMModelInfo(name=model_info.name, provider=model_info.provider)

    @staticmethod
    def serialize_list_registered_llms_grpc_response(grpc_response: llm_model_service_pb2.ListRegisteredLLMsResponse) -> ListRegisteredLLMsResponse:

        models = [RegisteredLLM(info=LLMModelInfo(name=model.info.name, provider=model.info.provider,
                                                  capabilities=LLMModelsClientGRPCHelper.serialize_grpc_llm_capabilities(model.info.capabilities)), 
                                endpoint=model.endpoint,
                                health_check=model.health_check,
                                status=model.status,
                                registered_at=model.registered_at,
                                adapter_type=model.adapter_type) for model in grpc_response.models]
        return ListRegisteredLLMsResponse(models=models)
    

    @staticmethod
    def get_llm_status_to_grpc(request: GetLLMStatusRequest) -> llm_model_service_pb2.GetLLMStatusRequest:
        return llm_model_service_pb2.GetLLMStatusRequest(name=request.name)
    
    @staticmethod
    def serialze_get_llm_status_grpc_response(grpc_response: llm_model_service_pb2.LLMStatusResponse) -> LLMStatusResponse:
        return LLMStatusResponse(name=grpc_response.name, status=grpc_response.status, endpoint=grpc_response.endpoint,
                                 last_checked=grpc_response.last_checked)
    
    
    def __init__(self):
        pass 



   

    
   
   

        

 
    




