"""This example illustrates how to send a simple chat request
"""

from loguru import logger
from rich import print as rich_print
from gogi.gogi import Gogi
from gogi.clients.models.index_config import IndexConfig



if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)


    # list indexes for a user
    response = platform.indexes.list_indexes(owner_name="user-123")
    rich_print(f"List indexes response: {response}")

    # create a new index. 
    # Documets can only be ingested into existing indexes, 
    # so this is a necessary step before we can add any documents.
    index_config = IndexConfig(
        name="my-first-doc-index",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=756,
        chunking_strategy="overlap",
        chunk_size=500,
        chunk_overlap=50,
        metadata_schema={"source": "pdf", "author": "John Doe"})
    
    # create the index
    response = platform.indexes.create_index(owner_name="user-123", config=index_config)
    rich_print(f"Create index response: {response}")

    # get the index we just created
    response = platform.indexes.get_index(index_name=response.name)
    rich_print(f"Get index response: {response}")

    # list the documents associated with the index.
    response = platform.documents.list_documents(index_name=response.name)
    rich_print(f"List documents response: {response}")

    response = platform.documents.get_document(index_name=response[0].index_name, 
                                               document_id=response[0].document_id)
    rich_print(f"Get document response: {response}")

    # delete a document
    response = platform.documents.delete_document(index_name=response.index_name, 
                                                  document_id=response.document_id)
    rich_print(f"Delete document response: {response}") 


    # finally, delete the index we created. 
    # This will also delete all documents contained within the index, so use with caution!
    response = platform.indexes.delete_index(index_name=index_config.name)
    rich_print(f"Delete index response: {response}")
