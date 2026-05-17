"""This example illustrates how to send a simple chat request
"""


from rich import print as rich_print
from gogi.genai_platform import GenAIPlatform
from gogi.llm_message import LLMessage, LLMMessageGroup
from gogi.llm_model_config import LLMModelConfig


if __name__ == '__main__':

    platform = GenAIPlatform(gateway_url="localhost:50051")


    messages = [{"role": "user", "content": "Who was Alexandr the Great?"}]
    model_config = LLMModelConfig(model="gpt-4o", provider="OpenAI")

    # TODO: A ModelClient mau need access to an API key
    response = platform.models.run(messages=LLMMessageGroup.build(messages),
                                   model_config=model_config)

    rich_print(response)
