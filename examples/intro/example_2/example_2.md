# Indexes, documents and ingestion

This example is a walkthrough of the typical workflow on the Gogi platform: create an index, ingest a document
into it, and wait for the ingestion to finish. It uses the `IndexesClient` (`platform.indexes`) and the
`DocumentsClient` (`platform.documents`).

| File            | What it does                                                                                   |
|-----------------|------------------------------------------------------------------------------------------------|
| `example_2.py`  | Creates an index, ingests a generated text document (a fictional company HR policy) and polls the ingestion job until it completes |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`
- The document ingestion workflow running, as ingestion happens asynchronously in the background

## Running the example

```bash
python examples/intro/example_2/example_2.py
```

## Walkthrough

### 1. Create an index

Documents can only be ingested into an existing index, so the example first lists the indexes of the owner
`user-123` with `platform.indexes.list_owner_indexes(owner_name=...)` and then creates one with
`platform.indexes.create_index(index_name="my-first-doc-index", owner_name="user-123")`.

An index only has a name, which must be unique within the deployment, and an owner. How documents are chunked
and embedded is not a property of the index: it is set for each document when the document is ingested (see
step 2). See example 1 for the other index operations.

The example then gets the new index by name (`get_index(index_name=...)`, which returns a `GogiIndex`) and
lists its documents, which is empty at this point.

### 2. Ingest a document

`create_temp_document()` writes a dummy document to a temporary file and returns its bytes. The document is a
fictional HR policy with specific, made-up facts (27 vacation days, a $67 meal allowance, the "Quasar Score",
...), which makes it easy to check later whether answers come from the document rather than the model's own
knowledge.

The document is described by an `IngestDocumentRequest`:

| Field               | Value in the example       | Meaning                                         |
|---------------------|----------------------------|-------------------------------------------------|
| `content`           | The document's bytes       | The raw document                                |
| `content_type`      | `UNKNOWN`                  | The document's content type                     |
| `index_name`        | `my-first-doc-index`       | The index to ingest the document into           |
| `document_id`       | A random UUID              | The document's unique id                        |
| `filename`          | `my_first_doc.txt`         | The original filename                           |
| `embeddings_client` | `sentence-transformer`     | The client used to compute the embeddings       |
| `embeddings_model`  | `clip`                     | The model used to embed the chunks              |
| `chunk_strategy`    | `fixed`                    | How the document is split into chunks           |
| `metadata`          | `format`, `author`, `source` | Custom metadata stored with the document      |

`platform.documents.ingest_document(request)` starts an asynchronous job that processes the document
(chunking, embedding, storing), so it returns the job rather than the document.
`platform.documents.get_document_ingest_job(job_id)` returns the job's current status.

### 3. Wait for the ingestion

The document can only be queried, or seen in the index's document list, once the job completes. How you wait
depends on your use case: you can poll the job status or be notified when the job is done. The example polls
with `wait_for_document_ingest(platform=..., job_id=..., poll_interval=5, timeout=300)`, which checks the job
every 5 seconds and gives up after 5 minutes.

### 4. Clean up (commented out)

The end of the example shows, commented out, how to get and delete the ingested document and then delete the
index. Deleting an index also deletes all the documents in it.

## Notes

- The document id must currently be a UUID.

## Driver code

The complete code of the example, `example_2.py`:

```python
"""This example illustrates the main endpoints of the Gogi platform, including index creation,
document ingestion, and querying.
It serves as a basic walkthrough of the typical workflow when interacting with the Gogi platform,
and demonstrates how to use the Python client to perform common operations.
"""

import tempfile
import uuid
from pathlib import Path

from loguru import logger
from rich import print as rich_print

from gogi.gogi import Gogi
from gogi.models.ingest_document import IngestDocumentRequest
from gogi.utils.document_ingestion_polling import wait_for_document_ingest

OWNER_NAME = "user-123"
INDEX_NAME = "my-first-doc-index"


def create_temp_document(filename: str) -> bytes:
    """Helper function to create a temporary PDF file for testing document ingestion."""

    file_content = """This is some dummy content for the PDF document.
    It can be as long as needed to simulate a real document, and can include multiple paragraphs, sections, etc.
    Date: June 1, 2026

    Section 1: Paid Time Off
    All full-time employees receive exactly 27 days of paid vacation per year.
    Unused vacation days roll over, but the maximum carryover is 8 days.
    Employees in the Zurich office receive an additional 3 floating holidays.

    Section 2: Remote Work
    Employees may work remotely up to 3 days per week. Wednesday is a
    mandatory in-office day for all teams. Remote work from outside the
    employee's home country requires written approval from the VP of People
    Operations, Priya Chandrasekaran, at least 14 business days in advance.

    Section 3: Expense Policy
    The daily meal allowance during business travel is $67 USD. Flights
    over 6 hours qualify for business class. Employees must submit
    expense reports within 11 calendar days of trip completion using the
    internal tool "SpendTrack 4.0".

    Section 4: Annual Bonus
    The annual bonus target is 14% of base salary for individual contributors
    and 19% for managers. Bonuses are paid in the March payroll cycle.
    The bonus multiplier is determined by the "Quasar Score", a proprietary
    performance rating on a scale of 0-150.

    Section 5: Pet Policy
    GloboTech allows dogs under 25 pounds in the Austin and Portland offices
    on Tuesdays and Thursdays only. All pets must be registered with Facilities
    using form GT-PET-2026. The Zurich and Singapore offices do not permit pets.
    """.strip()

    doc_path = Path(tempfile.mkdtemp()) / filename
    doc_path.write_text(file_content)
    return doc_path.read_bytes()


if __name__ == "__main__":
    # connect to the Gogi platform.
    # This will be the first step in any interaction with the platform, and will
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)

    # list the indexes of the owner
    indexes = platform.indexes.list_owner_indexes(owner_name=OWNER_NAME)
    rich_print(f"List indexes response: {indexes}")

    # create a new index.
    # Documents can only be ingested into existing indexes,
    # so this is a necessary step before we can add any documents.
    # An index only has a name and an owner; how its documents are chunked and
    # embedded is set per document when the document is ingested (see below).
    index = platform.indexes.create_index(index_name=INDEX_NAME, owner_name=OWNER_NAME)
    rich_print(f"Create index response: {index}")

    # get the index we just created
    index = platform.indexes.get_index(index_name=index.index_name)
    rich_print(f"Get index response: {index}")

    # list the documents associated with the index.
    # we shouldn't have any documents yet, so this should return an empty list.
    documents = platform.documents.list_documents(index_name=index.index_name)
    rich_print(f"List documents response: {documents}")

    doc_content = create_temp_document("my_first_doc.txt")

    # TODO: Right now we assume that document_id is UUID
    # This need not be the case
    ingest_request = IngestDocumentRequest(
        content=doc_content,
        content_type="UNKNOWN",
        index_name=index.index_name,
        document_id=uuid.uuid4().hex,
        filename="my_first_doc.txt",
        embeddings_model="clip",
        embeddings_client="sentence-transformer",
        chunk_strategy="fixed",
        metadata={"format": "txt", "author": "John Doe", "source": "generated"},
    )
    # ingest a document into the index.
    # This will kick off an asynchronous job to process the document (e.g., chunking, embedding, etc.),
    # so the response will contain information about the job status rather than the document itself.
    response = platform.documents.ingest_document(ingest_request)

    # Find out the job
    job = platform.documents.get_document_ingest_job(response.job_id)

    rich_print(f"Job status is {job.status}")

    # we need to wait for the ingest job to complete
    # before we can query the document or see it in the list of documents for the index.
    # How you hanlde this will depend on your specific use case and requirements - you could poll
    # the job status until it's complete, or you could set up a webhook to be notified when the
    # job is done, etc. For this example, we'll just do a simple polling loop with a sleep interval.
    result = wait_for_document_ingest(platform=platform, job_id=response.job_id, poll_interval=5, timeout=300)
    rich_print(f"Ingest document response: {result}")

    # document = platform.documents.get_document(index_name=result.index_name,
    #                                             document_id=result.document_id)
    # rich_print(f"Get document response: {document}")

    # # delete a document
    # deleted = platform.documents.delete_document(index_name=document.index_name,
    #                                              document_id=document.document_id)
    # rich_print(f"Delete document response: {deleted}")

    # # finally, delete the index we created.
    # # This will also delete all documents contained within the index, so use with caution!
    # deleted = platform.indexes.delete_index(index_name=index.index_name)
    # rich_print(f"Delete index response: {deleted}")
```
