from unittest.mock import MagicMock

import pytest

from gogi.clients.documents_client import DocumentsClient
from gogi.models.search_documents import SearchDocumentsRequest
from gogi.v1.data import document_service_pb2


@pytest.fixture
def client():
    # Avoid calling __init__ since it creates a gRPC channel.
    client = object.__new__(DocumentsClient)
    client.logger = None
    client._route_metadata = ()
    client._stub = MagicMock()
    return client


def _grpc_chunk(**overrides):
    defaults = {
        "chunk_id": "c-1",
        "document_id": "doc-1",
        "index_name": "idx",
        "content": "some text",
        "score": 0.87,
        "metadata": {"page": "3"},
    }
    defaults.update(overrides)
    return MagicMock(**defaults)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


def test_search_documents_calls_stub(client):
    client._stub.SearchDocuments.return_value = MagicMock(chunks=[])

    client.search_documents(
        SearchDocumentsRequest(
            index_name="idx",
            query="what is this about?",
            top_k=3,
            embeddings_model="text-embedding-3-small",
            embeddings_client="openai",
            document_ids=["doc-1"],
            metadata_filter={"lang": "en"},
        )
    )

    client._stub.SearchDocuments.assert_called_once()
    grpc_request = client._stub.SearchDocuments.call_args.args[0]
    assert grpc_request.index_name == "idx"
    assert grpc_request.query == "what is this about?"
    assert grpc_request.top_k == 3
    assert grpc_request.embeddings_model == "text-embedding-3-small"
    assert grpc_request.embeddings_client == "openai"
    assert list(grpc_request.document_ids) == ["doc-1"]
    assert dict(grpc_request.metadata_filter) == {"lang": "en"}


def test_search_documents_without_optional_filters(client):
    client._stub.SearchDocuments.return_value = MagicMock(chunks=[])

    client.search_documents(
        SearchDocumentsRequest(
            index_name="idx", query="q", embeddings_model="text-embedding-3-small", embeddings_client="openai"
        )
    )

    grpc_request = client._stub.SearchDocuments.call_args.args[0]
    assert grpc_request.top_k == 5
    assert list(grpc_request.document_ids) == []
    assert dict(grpc_request.metadata_filter) == {}


def test_search_documents_serializes_chunks(client):
    client._stub.SearchDocuments.return_value = MagicMock(
        chunks=[_grpc_chunk(), _grpc_chunk(chunk_id="c-2", score=0.5, metadata={})]
    )

    response = client.search_documents(
        SearchDocumentsRequest(
            index_name="idx", query="q", embeddings_model="text-embedding-3-small", embeddings_client="openai"
        )
    )

    assert [c.chunk_id for c in response.chunks] == ["c-1", "c-2"]
    assert response.chunks[0].content == "some text"
    assert response.chunks[0].score == 0.87
    assert response.chunks[0].metadata == {"page": "3"}
    assert response.chunks[1].metadata is None


def test_search_documents_rejects_non_positive_top_k():
    with pytest.raises(ValueError):
        SearchDocumentsRequest(index_name="idx", query="q", top_k=0, embeddings_model="m", embeddings_client="openai")


# ---------------------------------------------------------------------------
# the document registry
# ---------------------------------------------------------------------------


def _grpc_document(**overrides):
    defaults = {
        "document_id": "doc-1",
        "index_name": "maria--aeronautics",
        "filename": "fe-basics.txt",
        "chunk_count": 4,
        "metadata": {"subject": "numerical-methods", "topic": "finite-elements"},
        "content_type": "text/plain",
        "status": "COMPLETED",
        "job_id": "job-1",
        "created_at": "2026-10-16T10:00:00Z",
    }
    defaults.update(overrides)
    return document_service_pb2.DocumentMetadata(**defaults)


def test_list_documents_with_a_metadata_filter(client):
    client._stub.ListDocuments.return_value = document_service_pb2.ListDocumentsResponse(documents=[_grpc_document()])

    documents = client.list_documents("maria--aeronautics", metadata_filter={"subject": "numerical-methods"})

    request = client._stub.ListDocuments.call_args.args[0]
    assert request.index_name == "maria--aeronautics"
    assert dict(request.metadata_filter) == {"subject": "numerical-methods"}
    [document] = documents
    assert document.custom_metadata == {"subject": "numerical-methods", "topic": "finite-elements"}
    assert (document.status, document.job_id, document.content_type) == ("COMPLETED", "job-1", "text/plain")
    assert document.ingested_at.isoformat() == "2026-10-16T10:00:00+00:00"


def test_list_documents_without_a_filter(client):
    client._stub.ListDocuments.return_value = document_service_pb2.ListDocumentsResponse()

    assert client.list_documents("maria--aeronautics") == []
    assert dict(client._stub.ListDocuments.call_args.args[0].metadata_filter) == {}


def test_delete_document(client):
    client._stub.DeleteDocument.return_value = document_service_pb2.DeleteDocumentResponse(chunks_deleted=4)

    assert client.delete_document("maria--aeronautics", "doc-1") is True
    request = client._stub.DeleteDocument.call_args.args[0]
    assert (request.index_name, request.document_id) == ("maria--aeronautics", "doc-1")
