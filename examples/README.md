# Gogi Python SDK examples

These examples show how to use the Gogi Python SDK to work with the Gogi platform. Each example lives in its
own directory, with the code and a markdown file that discusses it.

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`
- The SDK installed (see the repository's [README](../README.md))

Some examples need more than that, for example provider API keys or a running workflow. Each example's
markdown file lists what it needs.

All examples start the same way, by connecting to the platform:

```python
from loguru import logger
from gogi.gogi import Gogi

platform = Gogi(gateway_url="localhost:50051", logger=logger)
```

The `Gogi` object gives access to all the clients: `platform.indexes`, `platform.documents`,
`platform.llm_clients`, `platform.prompts`, `platform.llm_session`, `platform.tools`, `platform.guardrails`
and `platform.workflows`.

## Intro examples

Short examples, one per client, in [`intro/`](intro).

| Example                                        | Client                                      | What it shows                                                                    |
|------------------------------------------------|---------------------------------------------|----------------------------------------------------------------------------------|
| [Example 1](intro/example_1/example_1.md)      | `IndexesClient` (`platform.indexes`)        | Create, get, list and delete indexes                                             |
| [Example 2](intro/example_2/example_2.md)      | `IndexesClient`, `DocumentsClient`          | Create an index, ingest a document and wait for the ingestion job                |
| [Example 3](intro/example_3/example_3.md)      | `LLMModelsClient` (`platform.llm_clients`)  | Send the same request to OpenAI and Anthropic (blocking and streamed); add Ollama as a new provider by registering a model |
| [Example 4](intro/example_4/example_4.md)      | `PromptsClient` (`platform.prompts`)        | Register, retrieve and delete a prompt with its metadata                         |
| [Example 5](intro/example_5/example_5.md)      | `LLMSessionsClient` (`platform.llm_session`)| Manage conversation sessions, their messages and memory                          |
| [Example 6](intro/example_6/example_6.md)      | `LLMToolsClient` (`platform.tools`)         | Register, discover, validate and execute tools; register an MCP server           |
| [Example 7](intro/example_7/example_7.md)      | `GuardrailsClient` (`platform.guardrails`)  | Validate input, filter output, check policies and report violations              |

Run an example from the repository root, e.g.

```bash
python examples/intro/example_1/example_1.py
```

## Agents

End-to-end agents that combine several services, in [`agents/`](agents).

| Example                                                       | What it shows                                                                                        |
|---------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| [Text summarization agent](agents/summarization/example.md)  | Upload a document, ingest it with a workflow, and summarize it with a RAG pipeline. Uses indexes, prompts, models, workflows and documents |

## Updating the intro examples

Each intro example's markdown file ends with a "Driver code" section, a copy of the example's code. After
changing an example's code, regenerate these sections from the repository root:

```bash
python scripts/update_driver_code.py
```

`python scripts/update_driver_code.py --check` changes nothing and exits with 1 if any section is out of date,
which is useful in CI.
