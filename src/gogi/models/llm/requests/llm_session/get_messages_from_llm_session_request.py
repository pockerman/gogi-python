from typing import Literal

from pydantic import BaseModel, Field

ContextStrategy = Literal["none", "truncate", "summarize", "hierarchical"]


class GetMessagesFromLLMSessionRequest(BaseModel):
    """Gets the messages of a session.

    Without a strategy, a page of the history, oldest first, with limit and offset. With a
    strategy, the context of the next model call within token_budget estimated tokens:

    - truncate: the most recent messages that fit (at most limit, if given)
    - summarize: a summary of the older messages, then the most recent ones
    - hierarchical: the user's memories, then the summary, then the most recent messages
    """

    session_id: str
    limit: int | None = Field(default=None, ge=0)
    offset: int | None = Field(default=None, ge=0)
    strategy: ContextStrategy | None = None
    # None means the platform's default budget
    token_budget: int | None = Field(default=None, gt=0)
    # what the summary must keep, e.g. "dates, prices and what was agreed"
    summary_focus: str | None = None
