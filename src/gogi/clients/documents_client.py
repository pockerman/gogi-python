from datetime import datetime

from gogi.clients.base_client import BaseClient
from gogi.models.document_metadata import DocumentMetadata
from gogi.models.document_section import DocumentSection, DocumentSectionContent
from gogi.models.ingest_document import IngestDocumentJob, IngestDocumentRequest
from gogi.models.search_documents import DocumentChunk, SearchDocumentsRequest, SearchDocumentsResponse
from gogi.v1.data import document_service_pb2, document_service_pb2_grpc

# each part of an upload stays well under gRPC's 4 MB message limit
UPLOAD_CHUNK_BYTES = 1024 * 1024


class DocumentsClient(BaseClient):
    @staticmethod
    def proto_to_doc_meta(resp) -> DocumentMetadata:
        return DocumentMetadata(
            document_id=resp.document_id,
            index_name=resp.index_name,
            filename=resp.filename,
            chunk_count=resp.chunk_count,
            page_count=resp.page_count if resp.page_count else None,
            word_count=resp.word_count if resp.word_count else None,
            custom_metadata=dict(resp.metadata),
            content_type=resp.content_type or None,
            status=resp.status or None,
            job_id=resp.job_id or None,
            size_bytes=resp.size_bytes,
            **({"ingested_at": datetime.fromisoformat(resp.created_at)} if resp.created_at else {}),
        )

    @staticmethod
    def proto_to_section(resp) -> DocumentSection:
        return DocumentSection(
            position=resp.position,
            title=resp.title,
            level=resp.level,
            page_start=resp.page_start or None,
            page_end=resp.page_end or None,
        )

    @staticmethod
    def proto_to_ingest_job(resp) -> IngestDocumentJob:
        return IngestDocumentJob(
            job_id=resp.job_id,
            index_name=resp.index_name,
            document_id=resp.document_id if resp.document_id else None,
            filename=resp.filename if resp.filename else None,
            status=resp.status,
            progress=resp.progress if resp.progress else None,
            error_message=resp.error_message if resp.error_message else None,
        )

    @staticmethod
    def proto_to_chunk(resp) -> DocumentChunk:
        return DocumentChunk(
            chunk_id=resp.chunk_id,
            document_id=resp.document_id,
            index_name=resp.index_name,
            content=resp.content,
            score=resp.score,
            metadata=dict(resp.metadata) if resp.metadata else None,
        )

    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="documents", logger=logger)
        self._stub = document_service_pb2_grpc.DocumentServerStub(self._channel)

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentMetadata]:
        """The documents of the index, optionally only those whose metadata has every key and value of
        ``metadata_filter``."""
        if self.logger:
            self.logger.debug(f"Listing documents for index: {index_name}")
        request = document_service_pb2.ListDocumentsRequest(index_name=index_name, metadata_filter=metadata_filter)
        resp = self._stub.ListDocuments(request, metadata=self.route_metadata)
        return [self.proto_to_doc_meta(d) for d in resp.documents]

    def get_document(self, index_name: str, document_id: str) -> DocumentMetadata:
        if self.logger:
            self.logger.debug(f"Getting document: {document_id} from index: {index_name}")

        request = document_service_pb2.GetDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.GetDocument(request, metadata=self.route_metadata)
        return self.proto_to_doc_meta(resp.document)

    def delete_document(self, index_name: str, document_id: str) -> bool:
        """Deletes the document and its chunks. Raises ``grpc.RpcError`` with ``NOT_FOUND`` if there's no such
        document."""
        if self.logger:
            self.logger.debug(f"Deleting document: {document_id} from index: {index_name}")
        request = document_service_pb2.DeleteDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.DeleteDocument(request, metadata=self.route_metadata)
        if self.logger:
            self.logger.debug(f"Deleted {resp.chunks_deleted} chunks of document {document_id}")
        return True

    def ingest_document(self, request: IngestDocumentRequest) -> IngestDocumentJob:
        """
        Ingest a document into the Gogi platform.
        This will create a new document associated with the specified index,
        and will kick off an asynchronous job to process the document (e.g., chunking, embedding, etc.).
        The content is streamed to the platform in parts of `UPLOAD_CHUNK_BYTES`, so documents larger
        than a single gRPC message (4 MB) can be ingested, up to the platform's upload limit.
        Args:
            request (IngestDocumentRequest): the index to ingest the document into, its filename, content,
                metadata, and how to chunk and embed it. The platform chooses the document_id if it's empty.
        Returns:
            IngestDocumentJob: An object representing the ingest job that was created to process the document.
            This includes information about the job status, progress, and any errors that may have occurred.
        """

        if self.logger:
            self.logger.debug(f"Ingesting document: {request.document_id} from index: {request.index_name}")

        info = document_service_pb2.IngestDocumentRequest(
            index_name=request.index_name,
            document_id=request.document_id,
            filename=request.filename,
            content_type=request.content_type,
            metadata=request.metadata,
            embeddings_client=request.embeddings_client,
            batch_size=request.batch_size,
            embeddings_model=request.embeddings_model,
            chunk_strategy=request.chunk_strategy,
            store_only=request.store_only,
            replace=request.replace,
        )
        resp = self._stub.UploadDocument(self._upload_parts(info, request.content), metadata=self.route_metadata)
        return self.proto_to_ingest_job(resp)

    @staticmethod
    def _upload_parts(info, content: bytes):
        """the document's details, then its content in parts"""
        yield document_service_pb2.UploadDocumentRequest(info=info)
        view = memoryview(content)
        for start in range(0, len(view), UPLOAD_CHUNK_BYTES):
            yield document_service_pb2.UploadDocumentRequest(chunk=bytes(view[start : start + UPLOAD_CHUNK_BYTES]))

    def list_sections(self, index_name: str, document_id: str) -> list[DocumentSection]:
        """The document's sections in order; a document has none until its ingestion has completed."""
        request = document_service_pb2.ListDocumentSectionsRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.ListDocumentSections(request, metadata=self.route_metadata)
        return [self.proto_to_section(section) for section in resp.sections]

    def get_section(
        self, index_name: str, document_id: str, position: int, include_subsections: bool = True
    ) -> list[DocumentSectionContent]:
        """The text of the section at the position, followed by its subsections' if include_subsections."""
        request = document_service_pb2.GetDocumentSectionRequest(
            index_name=index_name,
            document_id=document_id,
            position=position,
            include_subsections=include_subsections,
        )
        resp = self._stub.GetDocumentSection(request, metadata=self.route_metadata)
        return [
            DocumentSectionContent(section=self.proto_to_section(part.section), content=part.content)
            for part in resp.sections
        ]

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> tuple[DocumentMetadata, bytes]:
        """The document and its uploaded file, which the platform streams in parts: the whole file, or length bytes
        of it from offset (to its end if length is 0), e.g. for a video player seeking."""
        request = document_service_pb2.DownloadDocumentRequest(
            index_name=index_name, document_id=document_id, offset=offset, length=length
        )
        document, parts = None, []
        for message in self._stub.DownloadDocument(request, metadata=self.route_metadata):
            if message.HasField("document"):
                document = self.proto_to_doc_meta(message.document)
            else:
                parts.append(message.chunk)
        return document, b"".join(parts)

    def get_document_ingest_job(self, job_id: str) -> IngestDocumentJob:
        """
        Get the status of a document ingest job.
        Args:
            job_id (str): The unique identifier of the ingest job to check.
        Returns:
            IngestDocumentJob: An object representing the current status of the ingest job,
            including progress and any errors if applicable.
        """
        if self.logger:
            self.logger.debug(f"Getting document ingest status for job: {job_id}")

        request = document_service_pb2.GetIngestDocumentJobRequest(job_id=job_id)
        resp = self._stub.GetDocumentIngestJob(request, metadata=self.route_metadata)

        return self.proto_to_ingest_job(resp)

    def search_documents(self, request: SearchDocumentsRequest) -> SearchDocumentsResponse:
        """
        Retrieve the chunks of an index that are most similar to a query.
        The query is embedded server-side with the given embeddings client and model,
        so these must match the ones used when the documents were ingested.
        Args:
            request (SearchDocumentsRequest): The index to search, the query and the number of chunks to return.
        Returns:
            SearchDocumentsResponse: The matching chunks ordered by decreasing similarity score.
        """
        if self.logger:
            self.logger.debug(f"Searching index: {request.index_name} (top_k={request.top_k})")

        proto_request = document_service_pb2.SearchDocumentsRequest(
            index_name=request.index_name,
            query=request.query,
            top_k=request.top_k,
            embeddings_model=request.embeddings_model,
            embeddings_client=request.embeddings_client,
            document_ids=request.document_ids,
            metadata_filter=request.metadata_filter,
        )
        resp = self._stub.SearchDocuments(proto_request, metadata=self.route_metadata)
        return SearchDocumentsResponse(chunks=[self.proto_to_chunk(c) for c in resp.chunks])
