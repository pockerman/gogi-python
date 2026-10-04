"""Retrieval augmented generation (RAG) pipeline used by the summarization agent.

The pipeline has three steps:

1. Retrieve: search the agent's index for the chunks most similar to the user query.
   The platform embeds the query with the same OpenAI model the document was ingested with.
2. Augment: fill each registered prompt's declared parameters with the retrieved chunks and
   the user query, producing one chat message per prompt (in the order they were registered).
3. Generate: send the messages to an OpenAI chat model through the Gogi LLM gateway.
"""

import time

from prompts import RegisteredPrompt, fill
from pydantic import BaseModel

from gogi.gogi import Gogi
from gogi.models import LLMMessage, LLMRunRequest, LLMRunRequestConfig, LLMTokenUsage
from gogi.models.search_documents import DocumentChunk, SearchDocumentsRequest


class RAGResult(BaseModel):
    summary: str
    chunks: list[DocumentChunk]
    token_usage: LLMTokenUsage | None = None


class RAGPipeline:
    def __init__(
        self,
        platform: Gogi,
        index_name: str,
        prompts: list[RegisteredPrompt],
        llm_config: LLMRunRequestConfig,
        embeddings_client: str,
        embeddings_model: str,
        top_k: int = 8,
        min_score: float = 0.0,
    ):
        self.platform = platform
        self.index_name = index_name
        self.prompts = prompts
        self.llm_config = llm_config
        self.embeddings_client = embeddings_client
        self.embeddings_model = embeddings_model
        self.top_k = top_k
        self.min_score = min_score

    def retrieve(self, query: str, document_ids: list[str] | None = None) -> list[DocumentChunk]:
        response = self.platform.documents.search_documents(
            SearchDocumentsRequest(
                index_name=self.index_name,
                query=query,
                top_k=self.top_k,
                embeddings_client=self.embeddings_client,
                embeddings_model=self.embeddings_model,
                document_ids=document_ids,
            )
        )
        return [chunk for chunk in response.chunks if chunk.score >= self.min_score]

    def build_messages(self, query: str, chunks: list[DocumentChunk]) -> list[LLMMessage]:
        context = "\n\n".join(f"[{i}] {chunk.content.strip()}" for i, chunk in enumerate(chunks, start=1))
        values = {"context": context, "query": query}

        now = int(time.time())
        return [
            LLMMessage(role=prompt.spec.role, content=fill(prompt, values), timestamp=now) for prompt in self.prompts
        ]

    def run(self, query: str, document_ids: list[str] | None = None) -> RAGResult:
        chunks = self.retrieve(query=query, document_ids=document_ids)
        if not chunks:
            # nothing to ground the summary on; don't let the model make one up
            return RAGResult(summary="I could not find anything relevant to your request in the document.", chunks=[])

        response = self.platform.llm_clients.run(
            LLMRunRequest(config=self.llm_config, messages=self.build_messages(query=query, chunks=chunks))
        )
        return RAGResult(summary=response.content, chunks=chunks, token_usage=response.token_usage)
