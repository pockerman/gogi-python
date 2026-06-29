from gogi.v1 import prompt_service_pb2_grpc

from gogi.clients.base_client import BaseClient
from gogi.models.llm.requests.prompt_registration_request import PromptRegistrationRequest
from gogi.models.llm.requests.prompt_get_request import PromptGetRequest
from gogi.models.llm.requests.prompts_delete_request import PromptDeleteRequest

from gogi.models.llm.responses.prompt_registration_response import PromptRegistrationResponse
from gogi.models.llm.responses.prompt_get_response import PromptGetResponse
from gogi.models.llm.responses.prompt_delete_response import PromptDeleteResponse
from gogi.clients.grpc_helpers.prompts_client_grpc_helpers import PromptsClientGRPCHelper


class PromptsClient(BaseClient):

  
    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="prompts", logger=logger)
        self._grpc_helper = PromptsClientGRPCHelper()
        self._stub = prompt_service_pb2_grpc.PromptServerStub(self._channel)
        self._prompts_cache: dict[str, PromptGetResponse] = {}
        

 
    def register_prompt(self, request: PromptRegistrationRequest) -> PromptRegistrationResponse:
        grpc_request = self._grpc_helper.build_register_prompt_grpc_request(request=request)
        grpc_response = self._stub.RegisterPrompt(grpc_request, metadata=self.route_metadata)
        return self._grpc_helper.serialize_prompt_register_grpc_response(grpc_response=grpc_response)
    
    def get_prompt(self, request: PromptGetRequest) -> PromptGetResponse:

        if request.prompt_id in self._prompts_cache:
            return self._prompts_cache.get(request.prompt_id)

        grpc_request = self._grpc_helper.build_get_prompt_grpc_request(request=request)
        grpc_response = self._stub.GetPrompt(grpc_request, metadata=self.route_metadata)
        response = self._grpc_helper.serialize_get_prompt_grpc_response(grpc_response=grpc_response) 

        self._prompts_cache[request.prompt_id] = response
        return response 
    
    def delete_prompt(self, request: PromptDeleteRequest) -> PromptDeleteResponse:
        grpc_request = self._grpc_helper.build_delete_prompt_grpc_request(request=request)
        grpc_response = self._stub.DeletePrompt(grpc_request, metadata=self.route_metadata)
        response = self._grpc_helper.serialize_delete_prompt_grpc_response(grpc_response=grpc_response) 

        if request.prompt_id in self._prompts_cache:
            self._prompts_cache.pop(request.prompt_id)

        return response

    
        

 
    




