"""This example illustrates the LLMToolsClient in gogi.
The client allows users to: 

- Create a new session
- List all available sessions
- Add messages to a session
- Get the messages associated with a session
- Delete a sessions


"""


from loguru import logger
import time 
from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import AddMessagesToLLMSessionRequest
from gogi.models.llm.requests.llm_session.clear_user_llm_session_memory_request import ClearUserLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_memory_request import DeleteLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_request import DeleteLLMSessionRequest
from gogi.models.llm.requests.llm_session.get_llm_session_memory_request import GetLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.get_messages_from_llm_session_request import GetMessagesFromLLMSessionRequest
from gogi.models.llm.requests.llm_session.list_llm_session_request import ListLLMSessionsRequest
from gogi.models.llm.requests.llm_session.save_llm_session_memory_request import SaveLLMSessionMemoryRequest
from rich import print as rich_print

from gogi.models import CreateLLMSessionRequest

from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    



   



