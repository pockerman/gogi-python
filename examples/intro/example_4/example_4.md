# Prompts

In this example we use the `PromptsClient` (`platform.prompts`) to manage prompts in the Gogi prompt
registry. Storing prompts on the platform, together with their metadata, makes them versioned and shareable
instead of being hard-coded in each application.

| File            | What it does                                                                     |
|-----------------|----------------------------------------------------------------------------------|
| `example_4.py`  | Registers a customer support prompt, retrieves it by id and deletes it           |

## Prerequisites

- The Gogi platform running, with the gateway on `localhost:50051`

## Running the example

```bash
python examples/intro/example_4/example_4.py
```

## Walkthrough

### 1. Register a prompt

A `PromptRegistrationRequest` describes the prompt:

- `prompt_name` and `prompt_version` identify the prompt (`customer-support-agent`, `v1.0.0`)
- `gogi_index` is the index the prompt belongs to
- `content` is the prompt text, as bytes
- `metadata` (`PromptMetadata`) records
  - the `author` and the `model` the prompt was written for
  - the model `parameters` (`PromptParameters`): temperature, max tokens, stop sequences and penalties
  - the `test_info` (`PromptTestInfo`): the test set the prompt was evaluated on and the resulting metrics
    (accuracy, helpfulness, latency)

`platform.prompts.register_prompt(request=...)` registers the prompt and returns its `prompt_id`.

### 2. Retrieve the prompt

`platform.prompts.get_prompt(request=PromptGetRequest(prompt_id=...))` returns the registered prompt.

### 3. Delete the prompt

`platform.prompts.delete_prompt(request=PromptDeleteRequest(prompt_id=...))` removes the prompt from the
registry.

## Notes

The prompt metadata names the model `claude-sonnet-3.5`, which is not a valid Anthropic model id. The metadata
is only recorded, so the example runs, but use a model the platform supports (see example 3) if the prompt is
going to be sent to a model.
