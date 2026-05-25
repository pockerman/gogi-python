# gogi-python

Python SDK for <a href="https://github.com/pockerman/gogi">gogi[AI]</a> platform.

## Installation

- gogi is based on gRPC. Thus you will need the associated messages and services definitions.
Fetch the protos

```
git submodule update --remote --recursive
```

- Create a virtual environment for the SDK (do not install the SDK system-wide)
- Activate the virtual environment e.g.

```
conda create -n gogi-python-3.12 python=3.12 
conda activate gogi-python-3.12
```

- Install ```uv``` package manager using pip

```
pip install uv
```

- Build the protos

```
uv run python scripts/build_protos.py
```

- Build the package and install locally

```
uv build
uv pip install dist/*.whl
```

Checkout the ```examples``` directory for various use cases. Here is a quickstart.

```
from loguru import logger
import tempfile
from pathlib import Path
from rich import print as rich_print
from typing import Final

from gogi.gogi import Gogi
from gogi.clients.models.index_config import IndexConfig
from gogi.utils.document_ingestion_polling import wait_for_document_ingest


GOGI_GATEWAY_URL: Final[str] = "localhost:50051"


def create_temp_document(filename: str) -> bytes:
    """this is my document for ingestion""".strip()

    doc_path = Path(tempfile.mkdtemp()) / filename
    doc_path.write_text(file_content)
    return doc_path.read_bytes()


if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url=GOGI_GATEWAY_URL, logger=logger)


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
    # we shouldn't have any documents yet, so this should return an empty list.
    response = platform.documents.list_documents(index_name=response.name)
    rich_print(f"List documents response: {response}")


    doc_content = create_temp_document("my_first_doc.txt")

    # ingest a document into the index. 
    # This will kick off an asynchronous job to process the document (e.g., chunking, embedding, etc.), 
    # so the response will contain information about the job status rather than the document itself.
    response = platform.documents.ingest_document(index_name=index_config.name, 
                                                 document_id="my-first-doc",
                                                 filename="my_first_doc.txt",
                                                 content=doc_content,
                                                 metadata={"format": "txt", "author": "John Doe", "source": "generated"})
    
    # we need to wait for the ingest job to complete 
    # before we can query the document or see it in the list of documents for the index.
    # How you hanlde this will depend on your specific use case and requirements - you could poll the job status until it's complete,
    # or you could set up a webhook to be notified when the job is done, etc. For this example, we'll just do a simple polling loop with a sleep interval. 
    result = wait_for_document_ingest(platform=platform, job_id=response.job_id, 
                                      poll_interval=5, timeout=300)
    rich_print(f"Ingest document response: {result}")



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

```
