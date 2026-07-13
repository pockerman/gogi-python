"""This example illustrates the LLMSessionsClient in gogi.
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

    # create new session
    create_llm_session_response = platform.llm_session.get_or_create_session(request=CreateLLMSessionRequest(user_id="123"))
    rich_print(f"Create llm session response {create_llm_session_response}")

    # list the LLM sessions for this user
    list_sessions_response = platform.llm_session.list_sessions(request=ListLLMSessionsRequest(user_id="123"))
    rich_print(f"List llm sessions response {list_sessions_response}")

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
    rich_print(f"Add messages to llm sessions response {add_messages_to_session_response}")
    
    # get the messages
    get_session_messages_response = platform.llm_session.get_messages(request=GetMessagesFromLLMSessionRequest(session_id=create_llm_session_response.session_id,
                                                                                                               limit=10, offset=5))
    rich_print(f"Get messages from llm sessions response {get_session_messages_response}")


    # get the session memeory
    get_memory_response = platform.llm_session.get_memory(request=GetLLMSessionMemoryRequest(user_id='123', key='some-key',
                                                                                             session_id=create_llm_session_response.session_id))
    rich_print(f"Get llm session memory response {get_memory_response}")
    
    save_memory_response = platform.llm_session.save_memory(request=SaveLLMSessionMemoryRequest(user_id='123', key='some-key',
                                                                                             session_id=create_llm_session_response.session_id,
                                                                                             value="My-value"))
    rich_print(f"Save llm session memory response {save_memory_response}")
    

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





   



