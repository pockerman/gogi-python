# gogi-python

Python SDK for <a href="https://github.com/pockerman/gogi">gogi[AI]</a> platform.

## Installation

- Create a virtual environment for the SDK (do not install the SDK system-wide)
- Activate the virtual environment e.g.

```
conda create -n gogi-python-3.12 python=3.12
conda activate gogi-python-3.12
```

- Run the install script. It fetches the gRPC protos, installs the ```uv``` package manager,
builds the protobufs, and builds and installs the SDK into the project's ```.venv```:

```
./scripts/install.sh
```

## Examples

The [examples README](examples/README.md) lists all the available examples: short intro examples, one per
client (indexes, documents, models, prompts, sessions, tools and guardrails), and end-to-end agents. Each
example comes with a markdown file that discusses it.

## Quickstart

The quickstart below creates an index, ingests a short text document into it, waits for the ingestion to
finish, and then cleans up. It needs the Gogi platform running, with the gateway on `localhost:50051`.
[Example 2](examples/intro/example_2/example_2.md) walks through the same flow in more detail.

```python
import uuid
from typing import Final

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.models.ingest_document import IngestDocumentRequest
from gogi.utils.document_ingestion_polling import wait_for_document_ingest

GOGI_GATEWAY_URL: Final[str] = "localhost:50051"
OWNER_NAME: Final[str] = "user-123"
INDEX_NAME: Final[str] = "my-first-doc-index"


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, models, ...).
    platform = Gogi(gateway_url=GOGI_GATEWAY_URL, logger=logger)

    # create a new index.
    # Documents can only be ingested into existing indexes,
    # so this is a necessary step before we can add any documents.
    index = platform.indexes.create_index(index_name=INDEX_NAME, owner_name=OWNER_NAME)
    rich_print(f"Created index: {index}")

    # ingest a document into the index.
    # How the document is chunked and embedded is set per document.
    # This kicks off an asynchronous job to process the document (chunking, embedding, ...),
    # so the response is the ingestion job rather than the document itself.
    document_id = uuid.uuid4().hex
    job = platform.documents.ingest_document(
        IngestDocumentRequest(
            index_name=index.index_name,
            document_id=document_id,
            filename="my_first_doc.txt",
            content=b"This is my first document for ingestion.",
            content_type="UNKNOWN",
            embeddings_model="clip",
            embeddings_client="sentence-transformer",
            chunk_strategy="fixed",
            metadata={"format": "txt", "author": "John Doe"},
        )
    )

    # wait for the ingestion job to complete before using the document.
    # Here we poll the job status every 5 seconds, for up to 5 minutes.
    job = wait_for_document_ingest(platform=platform, job_id=job.job_id, poll_interval=5, timeout=300)
    rich_print(f"Ingestion job: {job}")

    document = platform.documents.get_document(index_name=index.index_name, document_id=document_id)
    rich_print(f"Document: {document}")

    # delete the document
    deleted = platform.documents.delete_document(index_name=index.index_name, document_id=document_id)
    rich_print(f"Deleted document: {deleted}")

    # finally, delete the index we created.
    # This also deletes all the documents in the index, so use with caution!
    deleted = platform.indexes.delete_index(index_name=index.index_name)
    rich_print(f"Deleted index: {deleted}")
```
