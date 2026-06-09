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
    list_response = platform.indexes.list_owner_indexes(owner_name="alex-corp")
    rich_print(f"List indexes response: {list_response}")

    # create the index
    create_response = platform.indexes.create_index(owner_name="alex-corp", index_name="my-index-2")
    rich_print(f"Create index response: {create_response}")

    # We can access an index either by name or id
    # get the index we just created
    get_response = platform.indexes.get_index(index_name=create_response.index_name)
    rich_print(f"Get index response by name: {get_response}")

    get_response = platform.indexes.get_index(index_id=get_response.index_id)
    rich_print(f"Get index response by id: {get_response}")

    # Similarly, indexes can be deleted by Id or name
    delete_response = platform.indexes.delete_index_by_id(get_response.index_id)
    rich_print(f"Delete index response by id: {delete_response}")

    # we have already deleted the index so this should be false
    delete_response = platform.indexes.delete_index_by_name(get_response.index_name)
    rich_print(f"Delete index response by name: {delete_response}")
    
    # delete all the owners indexes
    delete_response = platform.indexes.delete_owner_indexes(owner="alex-corp")
    rich_print(f"Delete index response by owner name: {delete_response}")



    
    

    



    