from unittest.mock import MagicMock

from gogi.clients.embeddings_client import EmbeddingsClient
from gogi.gogi import Gogi
from gogi.v1 import llm_model_service_pb2 as pb2


def _client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(EmbeddingsClient)
    client.logger = None
    client._route_metadata = (("authorization", "Bearer gogi_key"),)
    client._stub = MagicMock()
    return client


def test_list():
    client = _client()
    client._stub.ListEmbeddingModels.return_value = pb2.ListEmbeddingModelsResponse(
        models=[
            pb2.EmbeddingModel(name="bge-small-en-v1.5", dimensions=384, max_input_tokens=512, available=True),
            pb2.EmbeddingModel(name="text-embedding-3-small", dimensions=1536, credential_ref="openai"),
        ]
    )

    models = client.list()

    assert [(m.name, m.dimensions, m.available) for m in models] == [
        ("bge-small-en-v1.5", 384, True),
        ("text-embedding-3-small", 1536, False),
    ]
    assert models[1].credential_ref == "openai"
    assert ("authorization", "Bearer gogi_key") in client._stub.ListEmbeddingModels.call_args.kwargs["metadata"]


def test_register_a_model_the_application_hosts():
    client = _client()
    client._stub.RegisterEmbeddingModel.return_value = pb2.EmbeddingModel(
        name="nomic",
        dimensions=768,
        max_input_tokens=512,
        url="https://models.example.org/v1",
        credential_ref="models-key",
        available=True,
    )

    model = client.register(
        "nomic", "https://models.example.org/v1", served_name="nomic-embed-text", credential_ref="models-key"
    )

    assert (model.name, model.dimensions, model.url) == ("nomic", 768, "https://models.example.org/v1")
    request = client._stub.RegisterEmbeddingModel.call_args.args[0]
    assert (request.name, request.url, request.served_name, request.credential_ref) == (
        "nomic",
        "https://models.example.org/v1",
        "nomic-embed-text",
        "models-key",
    )


def test_embed():
    client = _client()
    client._stub.Embed.return_value = pb2.EmbedResponse(
        model="bge-small-en-v1.5",
        embeddings=[pb2.Embedding(values=[0.5, 0.25]), pb2.Embedding(values=[1.0, 0.0])],
    )

    vectors = client.embed("bge-small-en-v1.5", ["wing flutter", "shape functions"])

    assert vectors == [[0.5, 0.25], [1.0, 0.0]]
    request = client._stub.Embed.call_args.args[0]
    assert (request.model, list(request.inputs)) == ("bge-small-en-v1.5", ["wing flutter", "shape functions"])


def test_the_platform_gives_the_embeddings_client():
    gogi = Gogi(gateway_url="localhost:50051")

    assert gogi.embeddings is gogi.embeddings
