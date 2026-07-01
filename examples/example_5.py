"""This example illustrates the LLMSessionsClient in gogi.
The client allows users to: 

- Register new prompts
- Retrieve a prompt
- Delete a prompt


"""


from loguru import logger
import time 
from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import AddMessagesToLLMSessionRequest
from gogi.models.llm.requests.llm_session.clear_user_llm_session_memory_request import ClearUserLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_memory_request import DeleteLLMSessionMemoryRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_request import DeleteLLMSessionRequest
from rich import print as rich_print

from gogi.models import CreateLLMSessionRequest

from gogi.gogi import Gogi

if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # create new session
    create_llm_session_response = platform.llm_session.get_or_create_session(request=CreateLLMSessionRequest(user_id="123"))
    rich_print(f"Create llm session response {create_llm_session_response}")

    # add messages
    messages = [LLMMessage(
    role="user",
    content="What's the weather in London today?",
    timestamp=int(time.time()),), 
    LLMMessage(
    role="system",
    content="You are a helpful AI assistant.",
    timestamp=int(time.time()),)]
    add_messages_to_session_response = platform.llm_session.add_messages_to_session(request=AddMessagesToLLMSessionRequest(session_id=create_llm_session_response.session_id,
                                                                                                                           messages=messages))

    # delete the session
    delete_llm_session_response = platform.llm_session.delete_session(request=DeleteLLMSessionRequest(session_id=create_llm_session_response.session_id))
    rich_print(f"Delete llm session response {delete_llm_session_response}")


    # delete memory for the given session
    delete_session_memory_response = platform.llm_session.delete_memory(request=DeleteLLMSessionMemoryRequest(session_id=create_llm_session_response.session_id,
                                                                                                             key='some-key', user_id='123'))
    rich_print(f"Delete session memeory response {delete_session_memory_response}")

    # delete the user memory
    clear_user_memory_response = platform.llm_session.clear_user_memory(request=ClearUserLLMSessionMemoryRequest(user_id="123"))
    rich_print(f"Clear user memory response {clear_user_memory_response}")





   



