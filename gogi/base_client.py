import grpc 
from abc import ABC, abstractmethod
from .llm_model_config import LLMModelConfig
from .llm_message import LLMMessageGroup
from .llm_response import LLMResponse


class BaseClient:
    
    def __init__(self,  host: str):
        self.grpc_host = host
        self.channel = grpc.insecure_channel(host)

    @abstractmethod
    def run(self, model_config: LLMModelConfig, messages: LLMMessageGroup) -> LLMResponse:
        ...