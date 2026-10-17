from unittest.mock import MagicMock

import pytest

from gogi.clients.documents_client import DocumentsClient
from gogi.models.ingest_document import IngestDocumentRequest
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


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------


def _ingest(client, content: bytes, store_only: bool = False):
    sent = []

    def upload(parts, metadata):
        sent.extend(parts)
        return document_service_pb2.IngestDocumentJobResponse(job_id="job-1", index_name="idx", status="PENDING")

    client._stub.UploadDocument.side_effect = upload
    job = client.ingest_document(
        IngestDocumentRequest(
            index_name="maria--aeronautics",
            document_id="fe-basics",
            filename="fe-basics.pdf",
            content=content,
            content_type="application/pdf",
            metadata={"subject": "numerical-methods"},
            chunk_strategy="fixed",
            embeddings_model="clip",
            embeddings_client="sentence-transformer",
            store_only=store_only,
        )
    )
    return job, sent


def test_ingest_document_streams_the_details_then_the_content_in_parts(client, monkeypatch):
    monkeypatch.setattr("gogi.clients.documents_client.UPLOAD_CHUNK_BYTES", 4)

    job, sent = _ingest(client, b"0123456789")

    assert job.job_id == "job-1"
    info = sent[0].info
    assert (info.index_name, info.document_id, info.filename) == ("maria--aeronautics", "fe-basics", "fe-basics.pdf")
    assert dict(info.metadata) == {"subject": "numerical-methods"}
    assert info.content == b""
    assert [part.chunk for part in sent[1:]] == [b"0123", b"4567", b"89"]


def test_ingest_document_streams_a_large_document_in_parts_under_the_message_limit(client):
    content = b"x" * (5 * 1024 * 1024 + 1)

    _, sent = _ingest(client, content)

    assert all(len(part.chunk) <= 1024 * 1024 for part in sent[1:])
    assert b"".join(part.chunk for part in sent[1:]) == content


# ---------------------------------------------------------------------------
# sections and download
# ---------------------------------------------------------------------------


def _section(position, title, level, page_start=0, page_end=0):
    return document_service_pb2.DocumentSection(
        position=position, title=title, level=level, page_start=page_start, page_end=page_end
    )


def test_list_sections(client):
    client._stub.ListDocumentSections.return_value = document_service_pb2.ListDocumentSectionsResponse(
        sections=[_section(1, "Page 1", 1, 1, 1), _section(2, "2.1 Linear elements", 2)]
    )

    sections = client.list_sections("maria--aeronautics", "fem-notes")

    assert [(s.position, s.title, s.level, s.page_start) for s in sections] == [
        (1, "Page 1", 1, 1),
        (2, "2.1 Linear elements", 2, None),
    ]
    request = client._stub.ListDocumentSections.call_args.args[0]
    assert (request.index_name, request.document_id) == ("maria--aeronautics", "fem-notes")


def test_get_section_with_its_subsections(client):
    client._stub.GetDocumentSection.return_value = document_service_pb2.GetDocumentSectionResponse(
        sections=[
            document_service_pb2.DocumentSectionContent(section=_section(2, "2 Shape functions", 1), content="shape"),
            document_service_pb2.DocumentSectionContent(section=_section(3, "2.1 Linear", 2), content="linear"),
        ]
    )

    parts = client.get_section("maria--aeronautics", "fem-notes", 2)

    assert [(p.section.title, p.content) for p in parts] == [("2 Shape functions", "shape"), ("2.1 Linear", "linear")]
    request = client._stub.GetDocumentSection.call_args.args[0]
    assert (request.position, request.include_subsections) == (2, True)


def test_download_document_joins_its_parts(client):
    client._stub.DownloadDocument.return_value = iter(
        [
            document_service_pb2.DownloadDocumentResponse(
                document=document_service_pb2.DocumentMetadata(
                    document_id="fem-notes", index_name="maria--aeronautics", filename="fem-notes.md"
                )
            ),
            document_service_pb2.DownloadDocumentResponse(chunk=b"# 1 Intro"),
            document_service_pb2.DownloadDocumentResponse(chunk=b"duction\n"),
        ]
    )

    document, content = client.download_document("maria--aeronautics", "fem-notes")

    assert document.filename == "fem-notes.md"
    assert content == b"# 1 Introduction\n"


def test_download_part_of_a_document(client):
    client._stub.DownloadDocument.return_value = iter([])

    client.download_document("maria--aeronautics", "lecture-3", offset=100, length=50)

    request = client._stub.DownloadDocument.call_args.args[0]
    assert (request.offset, request.length) == (100, 50)


def test_ingest_a_document_without_ingesting_it(client):
    _, sent = _ingest(client, b"video bytes", store_only=True)

    assert sent[0].info.store_only is True
