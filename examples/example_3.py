"""This example illustrates the LLMModelClient in gogi.
The client allows users to 

- Provide access to LLM providers e.g. Anthropic, OpenAI
- Allow the user query the model capabilities
- Allow the user to register their own models
- Provide access to embedding models

"""

from loguru import logger


from gogi.clients.models.llm.requests.llm_capabilities_request import GetLLMCapabilitiesRequest
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.clients.models import (LLMRunRequest, 
                          LLMRunRequestConfig, 
                          LLMessage, LLMRegisterRequest, 
                          LLMModelInfo, LLMCapabilities,
                          ListRegisteredLLMsRequest, GetLLMStatusRequest)




if __name__ == '__main__':


    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # # get the providers the platform supports
    providers = platform.llm_clients.providers
    rich_print(f"Platform providers {providers}")

    # # check the models that a provider supports
    provider_models = platform.llm_clients.provider_models(provider="anthropic")
    rich_print(f"Platform providers models {provider_models}")

    # # asking for model request
    model_config = LLMRunRequestConfig(model="claude-sonnet-4.5", provider="anthropic", temperature=0.0, max_tokens=500)
    messages = [LLMessage(role="user", content="Who was Alexandr the Great?")]
    llm_run_request = LLMRunRequest(config=model_config, messages=messages)

    # # run a blocking request
    model_response = platform.llm_clients.run(llm_run_request)
    rich_print(f"Model response {model_response}")

    # # we can also stream the model response


    # # We can add a new model
    new_model_registration = LLMRegisterRequest(info=LLMModelInfo(name="my-model", provider="ollama",
                                                                  capabilities=LLMCapabilities(context_window=5000,
                                                                                               supports_json_mode=False,
                                                                                               supports_streaming=False,
                                                                                               supports_tools=True,
                                                                                               supports_vision=False)),
                                                endpoint="http://localhost:5000",
                                                health_check="http://localhost:5000/health",
                                                adapter_type=""
                                            )
    registration_response = platform.llm_clients.register_llm(new_model_registration)
    rich_print(f"Model registration response {registration_response}")

    # what models are registered:
    query_response = platform.llm_clients.list_registered_llms(ListRegisteredLLMsRequest())
    rich_print(f"Registered LLMs response {query_response}")

    # check the status of an LLM model
    query_response = platform.llm_clients.get_llm_status(GetLLMStatusRequest(name="my-model"))
    rich_print(f"LLM status response {query_response}")

    # get the capabilities of a model
    query_response = platform.llm_clients.get_llm_capabilities(GetLLMCapabilitiesRequest(model="my-model"))
    rich_print(f"LLM capabilties response {query_response}")



