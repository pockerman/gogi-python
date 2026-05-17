
from typing import override

from genai.v1 import chat_pb2, chat_pb2_grpc
from genai.v1 import common_pb2
from sdks.python_sdk.base_client import BaseClient
from sdks.python_sdk.llm_model_config import LLMModelConfig
from sdks.python_sdk.llm_message import LLMMessageGroup
from sdks.python_sdk.llm_response import LLMResponse

class ModelClient(BaseClient):
    
    def __init__(self, host: str):
        super().__init__(host=host)
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)

    @override
    def run(self, model_config: LLMModelConfig, messages: LLMMessageGroup) -> LLMResponse:
        # convert your internal message format → proto
        proto_messages = [
            common_pb2.ChatMessage(role=m.role, content=m.content)
            for m in messages.messages
        ]

        request = chat_pb2.ChatRequest(
            model=chat_pb2.ModelSpecifier(name=model_config.model, 
                                          provider=model_config.provider),
            messages=proto_messages,
            config=common_pb2.ChatConfig(
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
            ),
        )

        response = self.stub.Chat(request)

        # map proto → SDK response
        return LLMResponse(
            content=response.choices[0].message.content
        )