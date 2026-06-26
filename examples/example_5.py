"""This example illustrates the LLMSessionsClient in gogi.
The client allows users to: 

- Register new prompts
- Retrieve a prompt
- Delete a prompt


"""


from loguru import logger
from rich import print as rich_print


from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)




   



