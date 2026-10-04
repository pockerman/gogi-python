# Text summarization agent

In this example we will create a text summarization agent that utilizes Gogi as a platform for AI development.
The user uploads a document (e.g. a report or a book in PDF or text format). A workflow is triggered in the background
that embeds the document with OpenAI and stores it in an index owned by the user. Once the workflow is finished,
the user can ask for summaries of the document. The agent retrieves the relevant parts of the document with a RAG
pipeline and asks an OpenAI model to summarize them. Overall, this example shows you how to use collectively
the following services:

- Indexes
- Prompts
- Models
- Workflows
- Documents

## Architecture

```
            upload                                  create job
  user ─────────────► SummarizationAgent ──────────────────────────► Workflows
                         │        ▲                                      │
                         │        │ job completed                        ▼
                         │        └──────────────────────  ingest_document_workflow
                         │                                               │ ingest + embed (OpenAI)
                         │  summarize                                    ▼
                         └────────► RAGPipeline ── search ──────────►  Index (Documents)
                                        │
                                        │ prompts ◄────────────────── Prompts registry
                                        ▼
                                  LLM gateway (OpenAI) ──► summary
```

| File                           | What it does                                                                                    |
|--------------------------------|--------------------------------------------------------------------------------------------------|
| `agent.py`                     | The `SummarizationAgent` and the entry point. Registers the prompt file, creates the user index and the ingestion workflow |
| `summarization_prompts.toml`   | The default prompt file: one or more named, role-tagged prompt templates                        |
| `prompts.py`                   | Parses prompt files and registers/fetches their prompts with the Gogi prompt registry           |
| `ingestion_workflow.py`        | The `@workflow` that ingests a document into the index using OpenAI embeddings, and its job helpers |
| `rag_pipeline.py`              | Retrieve (`documents.search_documents`) → augment (fill each prompt's parameters) → generate (`llm_clients.run`) |

### Indexes

Every user gets their own index, `<owner>-summarization`, which is created the first time the agent runs.
All the documents the user uploads are ingested into it.

### Prompts

The caller supplies a prompt file in TOML (`--prompt-file`, defaulting to the bundled
`summarization_prompts.toml`). Each entry in the file declares:

- `name` — identifies the prompt in the Gogi prompt registry
- `role` — the chat role it plays when sent to the LLM (`system`, `user`, or `assistant`)
- `parameters` — the placeholder names the agent must substitute into it at request time
- `content` — the template text, using `{parameter}` placeholders

At startup the agent registers every prompt in the file with the Gogi prompt registry, fetches
each one back by id, and later fills in its declared parameters (`context`, `query`) to build
the chat messages sent to the LLM — one message per prompt entry, in file order. This way the
prompt set can be versioned, evaluated and swapped out without touching the agent code.

### Workflows

Embedding a document can take a while, so it runs as an asynchronous workflow declared with the `@workflow`
decorator. The agent registers the workflow once and creates a workflow job for every upload. The workflow asks
the document service to ingest the document, embedding its chunks with OpenAI's `text-embedding-3-small`,
reports its progress on the job and completes (or fails) the job when done.

By default the example executes the workflow in the same process for every job it creates, so you don't need to
deploy anything. Once the workflow is deployed on the platform, run the agent with `--deployed` and it will only
wait for the platform to process the job.

### RAG pipeline

When the user asks for a summary, the pipeline

1. **retrieves** the chunks most similar to the user request with `platform.documents.search_documents`.
   The query is embedded with the same OpenAI model the document was ingested with,
2. **augments** each registered prompt by filling in its declared parameters (the numbered chunks as
   `context`, the user request as `query`), and
3. **generates** the summary with an OpenAI chat model through `platform.llm_clients.run`.

If no chunk is retrieved, the pipeline answers that it found nothing relevant instead of letting the model guess.

## Running the example

Install this example's own dependencies (on top of the `gogi-python` SDK itself):

```
uv pip install -r examples/agents/summarization/requirements.txt
```

The example needs a running Gogi platform with

- an OpenAI API key configured for the LLM gateway and the embeddings client, and
- the `SearchDocuments` RPC of the document service.

```
python examples/agents/summarization/agent.py
python examples/agents/summarization/agent.py --file my_report.pdf --query "Summarize the main findings"
```

To use a different prompt set, write your own TOML file (see `summarization_prompts.toml` for the
format) and pass it with `--prompt-file`:

```
python examples/agents/summarization/agent.py --prompt-file my_prompts.toml
```

| Option / env var       | Default                    | Description                                              |
|------------------------|-----------------------------|----------------------------------------------------------|
| `--prompt-file`        | `summarization_prompts.toml` | TOML file declaring the prompts to register and use    |
| `--file`               | a sample handbook          | The document to upload                                   |
| `--query`              | `Summarize the document`   | What to summarize                                        |
| `--owner`              | `summarization-demo-user`  | The user that owns the index and the documents           |
| `--deployed`           | off                        | Don't run the ingestion workflow in-process               |
| `--llm-provider`       | `openai`                   | The LLM provider used to generate summaries               |
| `--embeddings-client`  | `openai`                   | The embeddings provider used to embed documents and queries |
| `--embeddings-model`   | `text-embedding-3-small`   | The embeddings model used to embed documents and queries. Must be the same at ingestion and retrieval time |
| `GOGI_GATEWAY_URL`     | `localhost:50051`          | The Gogi gateway                                         |
| `OPENAI_CHAT_MODEL`    | `gpt-4o-mini`              | The OpenAI model that writes the summary                 |
