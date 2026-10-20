import builtins

from gogi.clients.base_client import BaseClient
from gogi.models.embedding_model import EmbeddingModel
from gogi.v1 import llm_model_service_pb2 as pb2
from gogi.v1 import llm_model_service_pb2_grpc as pb2_grpc

# the models gogi provides: the two small ones it runs, and OpenAI's, used with the application's own key,
# stored as the credential "openai"
BGE_SMALL = "bge-small-en-v1.5"
MINILM = "all-MiniLM-L6-v2"
OPENAI_SMALL = "text-embedding-3-small"


def _model(model: pb2.EmbeddingModel) -> EmbeddingModel:
    return EmbeddingModel(
        name=model.name,
        dimensions=model.dimensions,
        max_input_tokens=model.max_input_tokens,
        url=model.url,
        credential_ref=model.credential_ref,
        available=model.available,
    )


class EmbeddingsClient(BaseClient):
    """The embedding models the application can use: those gogi provides, and those it hosts itself and
    registers by their URL. Documents are ingested and searched with them by name."""

    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="llms", logger=logger)
        self._stub = pb2_grpc.LLMModelServerStub(self._channel)

    def list(self) -> list[EmbeddingModel]:
        """The models gogi provides and the application's own."""
        response = self._stub.ListEmbeddingModels(pb2.ListEmbeddingModelsRequest(), metadata=self.route_metadata)
        return [_model(model) for model in response.models]

    def register(
        self, name: str, url: str, served_name: str = "", credential_ref: str = "", max_input_tokens: int = 0
    ) -> EmbeddingModel:
        """Registers a model the application hosts behind an OpenAI-compatible embeddings endpoint, e.g.
        ``register("nomic", "https://models.example.org/v1", served_name="nomic-embed-text")``. gogi calls it once
        to learn its dimensions, with the credential the application stored as ``credential_ref`` if it needs a
        key. Registering a name again replaces the registration; only the application can use the model."""
        response = self._stub.RegisterEmbeddingModel(
            pb2.RegisterEmbeddingModelRequest(
                name=name,
                url=url,
                served_name=served_name,
                credential_ref=credential_ref,
                max_input_tokens=max_input_tokens,
            ),
            metadata=self.route_metadata,
        )
        return _model(response)

    def embed(self, model: str, inputs: builtins.list[str]) -> builtins.list[builtins.list[float]]:
        """The vectors of the texts, in their order."""
        response = self._stub.Embed(pb2.EmbedRequest(model=model, inputs=inputs), metadata=self.route_metadata)
        return [list(embedding.values) for embedding in response.embeddings]
