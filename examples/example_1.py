"""This example illustrates how to send a simple chat request
"""


from rich import print as rich_print
from src.gogi import GoGi

if __name__ == '__main__':

    platform = GoGi(gateway_url="localhost:50051")




    rich_print(response)
