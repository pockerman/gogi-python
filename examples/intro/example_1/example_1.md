# Indexes

In this example we use the `IndexesClient` (`platform.indexes`) to manage indexes. An index is the logical unit
under which user data is organised in Gogi. Every index has a name, which must be unique within a Gogi
deployment, and an owner. An owner can own more than one index. Data can only be uploaded into an existing
index, so creating one is the first step before ingesting any documents.

| File            | What it does                                                                              |
|-----------------|-------------------------------------------------------------------------------------------|
| `example_1.py`  | Lists, creates, gets and deletes the indexes of the owner `alex-corp`                     |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`

## Running the example

```bash
python examples/intro/example_1/example_1.py
```

## Walkthrough

### 1. Connect to the platform

`Gogi(gateway_url="localhost:50051", logger=logger)` connects to the platform gateway. This is the first step
in any interaction with the platform; the `Gogi` object gives access to all the clients (indexes, documents,
models, ...).

### 2. List the owner's indexes

`platform.indexes.list_owner_indexes(owner_name="alex-corp")` returns the indexes the owner already has.

### 3. Create an index

`platform.indexes.create_index(owner_name="alex-corp", index_name="my-index-2")` creates a new index and
returns it as a `GogiIndex`.

### 4. Get an index

An index can be fetched either by name or by id with `platform.indexes.get_index(...)`, passing exactly one
of `index_name` or `index_id`.

### 5. Delete indexes

Indexes can also be deleted by id (`delete_index_by_id`) or by name (`delete_index_by_name`). Both return a
`bool`. The example deletes the same index twice, so the second call returns `False`.

Finally, `platform.indexes.delete_owner_indexes(owner="alex-corp")` deletes all the indexes of an owner.
