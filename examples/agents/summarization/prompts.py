"""Prompts used by the summarization agent.

The prompts are not hard-coded into the agent. Instead, they are registered with the
Gogi prompt registry and retrieved by id when the agent needs them. This way the prompts
can be versioned, evaluated and updated independently of the agent code.
"""

from dataclasses import dataclass

from gogi.gogi import Gogi
from gogi.models import (
    PromptGetRequest,
    PromptMetadata,
    PromptParameters,
    PromptRegistrationRequest,
    PromptTestInfo,
)

SYSTEM_PROMPT_NAME = "summarization-agent-system"
SUMMARY_PROMPT_NAME = "summarization-agent-summary"
PROMPT_VERSION = "v1.0.0"

SYSTEM_PROMPT = """
You are a precise summarization assistant.
You summarize documents using ONLY the excerpts you are given.
Never add facts that are not present in the excerpts.
If the excerpts do not contain enough information to answer, say so explicitly.
""".strip()

# {context} and {query} are filled in by the RAG pipeline at request time
SUMMARY_PROMPT_TEMPLATE = """
Below are excerpts retrieved from the user's document. Each excerpt is numbered.

<excerpts>
{context}
</excerpts>

User request: {query}

Write a concise summary that addresses the user request.
- Use short paragraphs or bullet points.
- Keep numbers, names and dates exactly as they appear in the excerpts.
- Cite the excerpts you used with their number, e.g. [2].
""".strip()


@dataclass(frozen=True)
class SummarizationPrompts:
    system: str
    summary_template: str


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


def register_prompts(platform: Gogi, index_name: str, author: str, model: str) -> dict[str, str]:
    """Register the agent prompts with the Gogi prompt registry.

    Returns:
        A mapping from prompt name to the prompt id assigned by the registry.
    """
    prompts = {
        SYSTEM_PROMPT_NAME: SYSTEM_PROMPT,
        SUMMARY_PROMPT_NAME: SUMMARY_PROMPT_TEMPLATE,
    }

    prompt_ids = {}
    for name, content in prompts.items():
        response = platform.prompts.register_prompt(
            request=PromptRegistrationRequest(
                prompt_name=name,
                prompt_version=PROMPT_VERSION,
                gogi_index=index_name,
                content=content.encode("utf-8"),
                metadata=_metadata(author=author, model=model),
            )
        )
        prompt_ids[name] = response.prompt_id
    return prompt_ids


def load_prompts(platform: Gogi, prompt_ids: dict[str, str]) -> SummarizationPrompts:
    """Fetch the agent prompts from the registry.
    The prompts client caches the prompts, so repeated calls do not hit the platform.
    """

    def _get(name: str) -> str:
        response = platform.prompts.get_prompt(request=PromptGetRequest(prompt_id=prompt_ids[name]))
        return response.content.decode("utf-8")

    return SummarizationPrompts(system=_get(SYSTEM_PROMPT_NAME), summary_template=_get(SUMMARY_PROMPT_NAME))
