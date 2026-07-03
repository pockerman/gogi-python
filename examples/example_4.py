"""This example illustrates the PromptsClient in gogi.
The client allows users to 

- Register new prompts
- Retrieve a prompt
- Delete a prompt


"""


from loguru import logger
from rich import print as rich_print

from gogi.models import (PromptRegistrationRequest, PromptTestInfo, PromptMetadata, PromptParameters,
                                 PromptGetRequest, 
                                 PromptDeleteRequest)
from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)




    prompt_request = PromptRegistrationRequest(
        prompt_name="customer-support-agent",
        prompt_version="v1.0.0",
        gogi_index="support-index",
        content=b"""
    You are a helpful customer support assistant.

    Always answer politely and concisely.
    Escalate billing issues to a human agent.
    """,
    metadata=PromptMetadata(
        author="alex",
        model="claude-sonnet-3.5",
        parameters=PromptParameters(
            temperature=0.2,
            max_tokens=4096,
            stop_sequences=["<END>"],
            frequency_penalty=0.0,
            presence_penalty=0.0,
        ),
        test_info=PromptTestInfo(
            test_set_id="customer-support-v1",
            test_set_path="/datasets/customer_support/test_set.json",
            metrics={
                "accuracy": 0.94,
                "helpfulness": 0.91,
                "latency_ms": 145.2,
            },
        ),
    ),
    )



    # register a new prompt
    request_response = platform.prompts.register_prompt(request=prompt_request)
    rich_print(f"Prompt registration request response {request_response}")

    # retrived the registered prompt
    retrieve_prompt_response = platform.prompts.get_prompt(request=PromptGetRequest(prompt_id=request_response.prompt_id))
    rich_print(f"Prompt get request response {request_response}")

    # delete the registered prompt
    delete_prompt_response = platform.prompts.delete_prompt(request=PromptDeleteRequest(prompt_id=retrieve_prompt_response.prompt_id))
    rich_print(f"Prompt delete request response {delete_prompt_response}")



