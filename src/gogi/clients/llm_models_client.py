from collections import defaultdict
from typing import Optional
from gogi.clients.base_client import BaseClient
from gogi.clients.models.llm_response import LLMResponse
from gogi.clients.models.llm_request import LLMRequest

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


    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="indexes", logger=logger)
        #self._stub = index_service_pb2_grpc.IndexServiceStub(self._channel)
        self._providers_to_model_cache: Optional[dict[str, list[str]]] = None

    def run(self, request: LLMRequest) -> LLMResponse:
        
        self.validate_provider_in_request(request=request, providers=self.providers)
        self.validate_provider_supports_model(request=request, models=self.provider_models(provider=request.config.provider))

        

    @property
    def providers(self) -> list[str]:
        if not self._providers_to_model_cache:
            pass 

        return list(self._providers_to_model_cache.keys())
    
    def provider_models(self, provider: str) -> list[str] | None:
  
        if provider not in self.providers:
            return None
        
        return self._providers_to_model_cache[provider]



