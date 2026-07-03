
from gogi.models.llm.requests.prompt_registration_request import PromptRegistrationRequest
from gogi.models.llm.requests.prompt_get_request import PromptGetRequest
from gogi.models.llm.requests.prompts_delete_request import PromptDeleteRequest

from gogi.models.llm.responses.prompt_registration_response import PromptRegistrationResponse
from gogi.models.llm.responses.prompt_get_response import PromptGetResponse
from gogi.models.llm.responses.prompt_delete_response import PromptDeleteResponse

from gogi.models.prompts.prompt_metadata import (
    PromptMetadata,
    PromptParameters,
    PromptTestInfo,
)

from gogi.v1 import prompt_service_pb2

__all__ = ['PromptsClientGRPCHelper']


class PromptsClientGRPCHelper:

    @staticmethod
    def build_register_prompt_grpc_request(
        request: PromptRegistrationRequest,
    ) -> prompt_service_pb2.PromptRegistrationRequest:

        return prompt_service_pb2.PromptRegistrationRequest(
            prompt_name=request.prompt_name,
            prompt_version=request.prompt_version,
            gogi_index=request.gogi_index,
            content=request.content,
            metadata=prompt_service_pb2.PromptMetadata(
                author=request.metadata.author,
                model=request.metadata.model,
                parameters=prompt_service_pb2.PromptParameters(
                    temperature=request.metadata.parameters.temperature,
                    max_tokens=request.metadata.parameters.max_tokens,
                    stop_sequences=request.metadata.parameters.stop_sequences,
                    frequency_penalty=request.metadata.parameters.frequency_penalty,
                    presence_penalty=request.metadata.parameters.presence_penalty,
                ),
                test_info=prompt_service_pb2.PromptTestInfo(
                    test_set_id=request.metadata.test_info.test_set_id,
                    test_set_path=request.metadata.test_info.test_set_path,
                    metrics=request.metadata.test_info.metrics,
                ),
            ),
        )

    @staticmethod
    def serialize_prompt_register_grpc_response(
        grpc_response: prompt_service_pb2.PromptRegistrationResponse,
    ) -> PromptRegistrationResponse:

        return PromptRegistrationResponse(
            prompt_id=grpc_response.prompt_id,
            #registered_at=grpc_response.registered_at.ToDatetime(),
        )

    @staticmethod
    def build_get_prompt_grpc_request(
        request: PromptGetRequest,
    ) -> prompt_service_pb2.PromptGetRequest:

        return prompt_service_pb2.PromptGetRequest(
            prompt_id=request.prompt_id
        )

    @staticmethod
    def serialize_get_prompt_grpc_response(
        grpc_response: prompt_service_pb2.PromptGetResponse,
    ) -> PromptGetResponse:

        return PromptGetResponse(
            prompt_id=grpc_response.prompt_id,
            prompt_name=grpc_response.prompt_name,
            prompt_version=grpc_response.prompt_version,
            gogi_index=grpc_response.gogi_index,
            content=grpc_response.content,
            metadata=PromptMetadata(
                author=grpc_response.metadata.author,
                model=grpc_response.metadata.model,
                parameters=PromptParameters(
                    temperature=grpc_response.metadata.parameters.temperature,
                    max_tokens=grpc_response.metadata.parameters.max_tokens,
                    stop_sequences=list(
                        grpc_response.metadata.parameters.stop_sequences
                    ),
                    frequency_penalty=grpc_response.metadata.parameters.frequency_penalty,
                    presence_penalty=grpc_response.metadata.parameters.presence_penalty,
                ),
                test_info=PromptTestInfo(
                    test_set_id=grpc_response.metadata.test_info.test_set_id,
                    test_set_path=grpc_response.metadata.test_info.test_set_path,
                    metrics=dict(
                        grpc_response.metadata.test_info.metrics
                    ),
                ),
            ),
        )

    @staticmethod
    def build_delete_prompt_grpc_request(
        request: PromptDeleteRequest,
    ) -> prompt_service_pb2.PromptDeleteRequest:

        return prompt_service_pb2.PromptDeleteRequest(
            prompt_id=request.prompt_id
        )

    @staticmethod
    def serialize_delete_prompt_grpc_response(
        grpc_response: prompt_service_pb2.PromptDeleteResponse,
    ) -> PromptDeleteResponse:

        return PromptDeleteResponse(
            deleted=grpc_response.deleted
        )

