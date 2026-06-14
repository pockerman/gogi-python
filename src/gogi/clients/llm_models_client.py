
from typing import Optional, List 
from gogi.clients.base_client import BaseClient
from gogi.clients.models.llm_response import LLMResponse
from gogi.clients.models.llm_request import LLMRequest
from gogi.clients.models.llm_message import LLMessage
from gogi.clients.models.llm_tool_definition import LLMToolDefinition
from gogi.clients.models.llm_run_request_config import LLMRunRequestConfig
from gogi.v1 import llm_model_service_pb2, llm_model_service_pb2_grpc



class LLMModelsClient(BaseClient):

    @staticmethod
    def validate_provider_in_request(request: LLMRequest, providers: list[str]) -> None:
        if request.config.provider not in providers:
            raise ValueError(f"Provider={request.config.provider} not in {providers}")
        
    @staticmethod
    def validate_provider_supports_model(request: LLMRequest, models: Optional[list[str]]) -> None:
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
        return [llm_model_service_pb2.ToolDefinition(type=tool.tool_type, function=tool.function) for tool in tools]
    
    @staticmethod
    def build_grpc_request(req: LLMRequest) -> llm_model_service_pb2.LLMRunRequest:
        messages = LLMModelsClient.request_messages_to_grpc_messages(messages=req.messages)
        config = LLMModelsClient.request_config_to_grpc_request_config(config=req.config)
        tools = LLMModelsClient.request_tools_to_grpcs_tools(tools=req.tools)
        response_format = llm_model_service_pb2.ResponseFormat(type=req.response_format.response_type, 
                                                               schema_json=req.response_format.response_schema_json) if req.response_format else None

        return llm_model_service_pb2.LLMRunRequest(messages=messages, config=config,
                                                   tools=tools, response_format=response_format)


    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="indexes", logger=logger)
        self._stub = llm_model_service_pb2_grpc.LLMModelServerStub(self._channel)
        self._providers_to_model_cache: Optional[dict[str, list[str]]] = None

    @property
    def providers(self) -> list[str]:
        if not self._providers_to_model_cache:
            pass 

        return list(self._providers_to_model_cache.keys())
    
    def provider_models(self, provider: str) -> list[str] | None:
        if provider not in self.providers:
            return None
        
        return self._providers_to_model_cache[provider]

    def run(self, request: LLMRequest) -> LLMResponse:
        
        self.validate_provider_in_request(request=request, providers=self.providers)
        self.validate_provider_supports_model(request=request, models=self.provider_models(provider=request.config.provider))

        grpc_request = self.build_grpc_request(req=request)
        response = self._stub.Run(grpc_request)

        return LLMResponse(content=response.content, model=response.model,
                           provider=response.provider,
                           finish_reason=response.finish_reason,
                           token_usage=response.usage, tool_calls=response.tool_calls
                           )

        

 
    




