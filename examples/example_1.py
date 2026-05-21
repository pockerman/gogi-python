"""This example illustrates how to send a simple chat request
"""


from rich import print as rich_print
from gogi.gogi import GoGi

if __name__ == '__main__':

    platform = GoGi(gateway_url="localhost:50051")

    response = platform.documents.list_documents(index_name="my-first-doc-index")
    rich_print(response)
