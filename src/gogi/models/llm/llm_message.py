from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from gogi.models.llm.llm_tool_definition import LLMToolCall


class LLMImage(BaseModel):
    """An image for a model: its bytes, or a document of the platform's, e.g. a photo uploaded with
    ``store_only``, which the platform reads itself, so a large image needn't travel in the request."""

    data: bytes | None = None
    # the index and id of the document that holds the image
    index_name: str | None = None
    document_id: str | None = None
    # image/jpeg, image/png, image/gif or image/webp; the platform works it out if empty
    media_type: str = ""

    @model_validator(mode="after")
    def _one_source(self) -> Self:
        if (self.data is None) == (self.document_id is None):
            raise ValueError("an image is either its data or a document")
        if self.document_id is not None and not self.index_name:
            raise ValueError("an image's document needs its index_name")
        return self


class LLMContentPart(BaseModel):
    """A part of a user message's content: text or an image."""

    text: str | None = None
    image: LLMImage | None = None


class LLMMessage(BaseModel):
    """A message of a conversation with a model.

    An assistant message has the tools the model called, if any, in ``tool_calls``. A ``tool``
    message gives the model the result of one of those calls: ``tool_call_id`` is the id of the
    call and ``content`` its result.
    """

    role: Literal["user", "system", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None
    timestamp: int = 0
    # a user message's text and images, in order, after its content
    parts: list[LLMContentPart] = Field(default_factory=list)

    @classmethod
    def user_with_images(cls, text: str, images: list[LLMImage]) -> Self:
        """A user message asking about images, e.g. "What defects do you see?" and a photo."""
        return cls(role="user", content=text, parts=[LLMContentPart(image=image) for image in images])

    @classmethod
    def tool_result(cls, tool_call: LLMToolCall, content: str) -> Self:
        """The message that gives the model the result of one of its tool calls."""
        return cls(role="tool", content=content, tool_call_id=tool_call.idx, name=tool_call.function.name)


class LLMMessageGroup(BaseModel):
    messages: list[LLMMessage]

    @classmethod
    def build(cls, messages: list[dict[str, str]]) -> Self:
        return cls(messages=messages)
