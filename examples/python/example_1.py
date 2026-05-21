"""This example illustrates how to send a simple chat request
"""


from rich import print as rich_print
from gogi.gogi import GoGi
from gogi.llm_message import LLMessage, LLMMessageGroup
from gogi.llm_model_config import LLMModelConfig


if __name__ == '__main__':

    platform = GoGi(gateway_url="localhost:50051")




    rich_print(response)
