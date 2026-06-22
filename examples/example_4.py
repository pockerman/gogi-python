"""This example illustrates the PromptsClient in gogi.
The client allows users to 

- Register new prompts
- Retrieve a prompt
- Delete a prompt


"""


from loguru import logger
from rich import print as rich_print

from gogi.clients.models import (PromptRegistrationRequest, 
                                 PromptGetRequest, 
                                 PromptDeleteRequest)
from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # register a new prompt
    request_response = platform.prompts.register_prompt(request=PromptRegistrationRequest())
    rich_print(f"Prompt registration request response {request_response}")

    # retrived the registered prompt
    retrieve_prompt_response = platform.prompts.get_prompt(request=PromptGetRequest(prompt_id=request_response.prompt_id))
    rich_print(f"Prompt get request response {request_response}")

    # delete the registered prompt
    delete_prompt_response = platform.prompts.delete_prompt(request=PromptDeleteRequest(prompt_id=retrieve_prompt_response.prompt_id))
    rich_print(f"Prompt delete request response {delete_prompt_response}")



