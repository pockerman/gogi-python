"""This example illustrates indexes in gogi 
Indexes in gogi represent a logical unit under which user data is organised.
An index has to have a unique name under a gogi deployment and an owner.
An owner can own more than one indices. Before uploading data via gogi you need
to create an index under which the data will exist

"""

from loguru import logger
import tempfile
from pathlib import Path
from rich import print as rich_print
import uuid

from gogi.gogi import Gogi
from gogi.clients.models.index_config import IndexConfig
from gogi.clients.models.ingest_document import IngestDocumentRequest
from gogi.utils.document_ingestion_polling import wait_for_document_ingest






if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)


    # list indexes for a user
    response = platform.indexes.list_owner_indexes(owner_name="alex-corp")
    rich_print(f"List indexes response: {response}")

    
    
    # create the index
    response = platform.indexes.create_index(owner_name="alex-corp", index_name="my-index-2")
    rich_print(f"Create index response: {response}")

    # We can access an index either by name or id
    # get the index we just created
    response = platform.indexes.get_index(index_name=response.index_name)
    rich_print(f"Get index response: {response}")

    response = platform.indexes.get_index(index_id=response.index_id)
    rich_print(f"Get index response: {response}")




    
    

    



    