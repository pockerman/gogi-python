"""This example illustrates the LLMModelClient in gogi.
The client allows users to 

- Provide access to LLM providers e.g. Anthropic, OpenAI
- Allow the user query the model capabilities
- Allow the user to register their own models
- Provide access to embedding models

"""

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.clients import LLMRequest, LLMRunRequestConfig, LLMessage




if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # get the providers the platform supports
    providers = platform.llm_clients.providers

    rich_print(f"Platform providers {providers}")

    # check the models that a provider supports
    provider_models = platform.llm_clients.provider_models(provider="anthropic")
    rich_print(f"Platform providers models {provider_models}")

    # asking for model request
    model_config = LLMRunRequestConfig(model="claude-sonnet-4.5", provider="anthropic", temperature=0.0, max_tokens=500)
    messages = [LLMessage(role="user", content="Who was Alexandr the Great?")]
    llm_run_request = LLMRequest(config=model_config, messages=messages)

    # run a blocking request
    model_response = platform.llm_clients.run(llm_run_request)
    rich_print(f"Model response {model_response}")



