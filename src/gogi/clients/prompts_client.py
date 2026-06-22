
from typing import Optional, List, Iterator
import grpc 

from gogi.clients.base_client import BaseClient
from gogi.clients.models.llm.requests.prompt_registration_request import PromptRegistrationRequest
from gogi.clients.models.llm.requests.prompt_get_request import PromptGetRequest
from gogi.clients.models.llm.requests.prompts_delete_request import PromptDeleteRequest

from gogi.clients.models.llm.responses.prompt_registration_response import PromptRegistrationResponse
from gogi.clients.models.llm.responses.prompt_get_response import PromptGetResponse
from gogi.clients.models.llm.responses.prompt_delete_response import PromptDeleteResponse






class PromptsClient(BaseClient):

  
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llms", logger=logger)
        self._stub = llm_model_service_pb2_grpc.LLMModelServerStub(self._channel)
        self._providers_to_model_cache: Optional[dict[str, list[str]]] = None

 
    def register_prompt(self, request: PromptRegistrationRequest) -> PromptRegistrationResponse:
        
       pass
    
    def get_prompt(self, request: PromptGetRequest) -> PromptGetResponse:
        pass 
    
    def delete_prompt(self, request: PromptDeleteRequest) -> PromptDeleteResponse:
        pass 

    
        

 
    




