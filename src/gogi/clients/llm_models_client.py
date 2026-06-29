
from typing import Optional, List, Iterator
import grpc 

from gogi.clients.base_client import BaseClient
from gogi.models.llm.requests.list_llms_request import ListLLMsRequest
from gogi.models.llm.requests.llm_capabilities_request import GetLLMCapabilitiesRequest
from gogi.models.llm.requests.llm_register_request import LLMRegisterRequest
from gogi.models.llm.requests.llm_request_status import GetLLMStatusRequest
from gogi.models.llm.requests.llm_run_request import LLMRunRequest
from gogi.models.llm.requests.list_registered_llm_request import ListRegisteredLLMsRequest
from gogi.models.llm.responses.list_llms_response import ListLLMsResponse
from gogi.models.llm.responses.llm_capabilities_response import LLMCapabilitiesResponse
from gogi.models.llm.responses.llm_run_response import LLMRunResponse
from gogi.models.llm.responses.llm_register_response import LLMRegisterResponse
from gogi.models.llm.responses.list_registered_llms_response import ListRegisteredLLMsResponse
from gogi.models.llm.responses.llm_run_stream_chunk import LLMRunStreamChunk
from gogi.models.llm.llm_token_usage import LLMTokenUsage
from gogi.models.llm.llm_provider import LLMProvider

from gogi.clients.grpc_helpers.llm_models_client_grpc_helpers import LLMModelsClientGRPCHelper
from gogi.models.llm.responses.llm_status_response import LLMStatusResponse
from gogi.v1 import llm_model_service_pb2, llm_model_service_pb2_grpc



class LLMModelsClient(BaseClient):

  
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llms", logger=logger)
        self._grpc_helper = LLMModelsClientGRPCHelper()
        self._stub = llm_model_service_pb2_grpc.LLMModelServerStub(self._channel)
        self._providers_to_model_cache: Optional[dict[str, list[str]]] = None

    @property
    def providers(self) -> list[str]:
        if not self._providers_to_model_cache:
            self.get_llm_providers()

        return list(self._providers_to_model_cache.keys())
    
    def provider_models(self, provider: str) -> list[str] | None:
        if provider not in self.providers:
            return None
        
        return self._providers_to_model_cache[provider]

    def run(self, request: LLMRunRequest) -> LLMRunResponse:
        
        self._grpc_helper.validate_provider_in_request(request=request, providers=self.providers)
        self._grpc_helper.validate_provider_supports_model(request=request, models=self.provider_models(provider=request.config.provider))

        grpc_request = self._grpc_helper.build_grpc_request(req=request)
        response = self._stub.Run(grpc_request, metadata=self.route_metadata)

        return LLMRunResponse(content=response.content, model=response.model,
                           provider=response.provider,
                           finish_reason=response.finish_reason,
                           token_usage=self._grpc_helper.grpc_token_usage_to_token_usage(response.usage), 
                           tool_calls=self._grpc_helper.grpc_tool_calls_to_tool_call(response.tool_calls)
                           )
    
    def run_stream(self, request: LLMRunRequest) -> Iterator[LLMRunStreamChunk]:
        grpc_request = self._grpc_helper.build_grpc_request(request)

        try:
            for chunk in self._stub.RunStream(grpc_request, metadata=self.route_metadata):
                    usage = None
                    if chunk.HasField("usage"):
                        usage = LLMTokenUsage(
                            prompt_tokens=chunk.usage.prompt_tokens,
                            completion_tokens=chunk.usage.completion_tokens,
                            total_tokens=chunk.usage.total_tokens,
                        )
                    yield LLMRunStreamChunk(
                        token=chunk.token,
                        model=chunk.model,
                        finish_reason=chunk.finish_reason
                        if chunk.HasField("finish_reason")
                        else None,
                        usage=usage,
                    )
            return  # stream completed successfully
        except grpc.RpcError as e:
            last_error = e
            if self._should_fail_fast(e, fallback_config):
                raise
            if self.logger:
                self.logger.warning("chat_stream failed for model %s: %s", try_model, e)
            pass 
        raise last_error
    
    def list_llms(self, request: ListLLMsRequest) -> ListLLMsResponse:
        grpc_request = self._grpc_helper.list_llms_request_to_grpc(request)
        grpc_response = self._stub.ListLLMs(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialze_list_llms_grpc_response(grpc_response)

    def get_llm_capabilities(self, request: GetLLMCapabilitiesRequest) -> LLMCapabilitiesResponse:
        grpc_request = self._grpc_helper.get_llm_capabilities_to_grpc(request)
        grpc_response = self._stub.GetLLMCapabilities(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialze_get_llm_capabilities_grpc_response(grpc_response)

    
    def get_llm_providers(self) -> List[LLMProvider]:
        response = self._stub.GetLLMProviders(llm_model_service_pb2.GetLLMProvidersRequest(fetch_models=True), 
                                              metadata=self.route_metadata)
        providers = [LLMProvider(name=provider.name, models=provider.models) for provider in response.providers]

        self._providers_to_model_cache = {}
        for p in providers:
            self._providers_to_model_cache[p.name] = p.models
        return providers
    
    def register_llm(self, request: LLMRegisterRequest) -> LLMRegisterResponse:

        grpc_request = self._grpc_helper.build_grpc_registration_request(request)
        grpc_response = self._stub.RegisterLLM(grpc_request, metadata=self.route_metadata)

        return LLMRegisterResponse(name=grpc_response.name, 
                                   status=grpc_response.status, 
                                   registered_at=grpc_response.registered_at)
    
    def list_registered_llms(self, request: ListRegisteredLLMsRequest) -> ListRegisteredLLMsResponse:
        grpc_request = self._grpc_helper.list_registered_llms_request_to_grpc(request)
        grpc_response = self._stub.ListRegisteredLLMs(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_list_registered_llms_grpc_response(grpc_response)
    
    def get_llm_status(self, request: GetLLMStatusRequest) -> LLMStatusResponse:
        grpc_request = self._grpc_helper.get_llm_status_to_grpc(request)
        grpc_response = self._stub.GetLLMStatus(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialze_get_llm_status_grpc_response(grpc_response)

        

 
    




