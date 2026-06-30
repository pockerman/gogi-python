"""This example illustrates the LLMSessionsClient in gogi.
The client allows users to: 

- Register new prompts
- Retrieve a prompt
- Delete a prompt


"""


from loguru import logger
from rich import print as rich_print

from gogi.models import CreateLLMSessionRequest

from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # create new session
    create_llm_session_req = platform.llm_session.get_or_create_session(request=CreateLLMSessionRequest(user_id="123"))
    rich_print(f"Create llm session response {create_llm_session_req}")





   



