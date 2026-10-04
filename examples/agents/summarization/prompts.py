"""Prompt handling for the summarization agent.

Prompts are not hard-coded into the agent. Instead, the caller supplies a prompt file (TOML)
that lists one or more prompts, each with:

- name: identifies it in the Gogi prompt registry
- role: the chat role it plays when sent to the LLM ("system", "user", "assistant")
- parameters: the placeholder names the agent must substitute into its content at request time
- content: the template text, using {parameter} placeholders

The agent registers every prompt in the file with the Gogi prompt registry, fetches it back
by id, and uses the fetched content (with its declared parameters filled in) to build the
chat messages sent to the LLM. See summarization_prompts.toml for the default prompt set.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from gogi.gogi import Gogi
from gogi.models import (
    PromptGetRequest,
    PromptMetadata,
    PromptParameters,
    PromptRegistrationRequest,
    PromptTestInfo,
)


@dataclass(frozen=True)
class PromptSpec:
    name: str
    role: str
    parameters: list[str]
    content: str


@dataclass(frozen=True)
class RegisteredPrompt:
    spec: PromptSpec
    prompt_id: str
    content: str  # fetched back from the registry after registration


def load_prompt_file(path: Path) -> tuple[str, list[PromptSpec]]:
    """Parse a TOML prompt file. Returns (version, specs)."""
    with path.open("rb") as f:
        data = tomllib.load(f)

    specs = [
        PromptSpec(
            name=p["name"],
            role=p["role"],
            parameters=list(p.get("parameters", [])),
            content=p["content"],
        )
        for p in data["prompts"]
    ]
    return data["version"], specs


def _metadata(author: str, model: str) -> PromptMetadata:
    return PromptMetadata(
        author=author,
        model=model,
        parameters=PromptParameters(
            temperature=0.1,
            max_tokens=1000,
            stop_sequences=[],
            frequency_penalty=0.0,
            presence_penalty=0.0,
        ),
        # no evaluation has been run for these prompts yet
        test_info=PromptTestInfo(test_set_id="summarization-agent-v1", test_set_path="", metrics={}),
    )


def register_prompts(
    platform: Gogi,
    specs: list[PromptSpec],
    version: str,
    author: str,
    model: str,
    gogi_index: str,
) -> list[RegisteredPrompt]:
    """Register every prompt in the file with the Gogi prompt registry and fetch it back.

    Returns the registered prompts in the same order as ``specs``, which is also the order
    the corresponding chat messages are sent to the LLM in.
    """
    registered = []
    for spec in specs:
        response = platform.prompts.register_prompt(
            request=PromptRegistrationRequest(
                prompt_name=spec.name,
                prompt_version=version,
                gogi_index=gogi_index,
                content=spec.content.encode("utf-8"),
                metadata=_metadata(author=author, model=model),
            )
        )
        fetched = platform.prompts.get_prompt(request=PromptGetRequest(prompt_id=response.prompt_id))
        registered.append(
            RegisteredPrompt(spec=spec, prompt_id=response.prompt_id, content=fetched.content.decode("utf-8"))
        )
    return registered


def fill(prompt: RegisteredPrompt, values: dict[str, str]) -> str:
    """Substitute a registered prompt's declared parameters into its content."""
    missing = [name for name in prompt.spec.parameters if name not in values]
    if missing:
        raise ValueError(f"Missing values for prompt {prompt.spec.name!r} parameters: {missing}")
    return prompt.content.format(**{name: values[name] for name in prompt.spec.parameters})
