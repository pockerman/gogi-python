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
