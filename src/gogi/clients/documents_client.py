from typing import List, Optional
from pathlib import Path

from gogi.clients.models.document_metadata import DocumentMetadata
from gogi.clients.models.ingest_document import IngestDocumentJob, IngestDocumentRequest
from gogi.clients.base_client import BaseClient
from gogi.v1.data import document_service_pb2
from gogi.v1.data import document_service_pb2_grpc


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
            custom_metadata=None,
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


    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="documents", logger=logger)
        self._stub = document_service_pb2_grpc.DocumentServerStub(self._channel)

    def list_documents(self, index_name: str) -> List[DocumentMetadata]:
        if self.logger:
            self.logger.debug(f"Listing documents for index: {index_name}")
        request = document_service_pb2.ListDocumentsRequest(index_name=index_name)
        resp = self._stub.ListDocuments(request, metadata=self.route_metadata)
        return [self.proto_to_doc_meta(d) for d in resp.documents]

    def get_document(self, index_name: str, document_id: str) -> DocumentMetadata:
        if self.logger:
            self.logger.debug(f"Getting document: {document_id} from index: {index_name}")

        request = document_service_pb2.GetDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.GetDocument(request, metadata=self.route_metadata)
        return self.proto_to_doc_meta(resp.document)

    def delete_document(self, index_name: str, document_id: str) -> bool:
        if self.logger:
            self.logger.debug(f"Deleting document: {document_id} from index: {index_name}")
        request = document_service_pb2.DeleteDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.DeleteDocument(request, metadata=self.route_metadata)
        return resp.response
    
    def ingest_document(self,request: IngestDocumentRequest) -> IngestDocumentJob:
        """
        Ingest a document into the Gogi platform. 
        This will create a new document associated with the specified index, 
        and will kick off an asynchronous job to process the document (e.g., chunking, embedding, etc.).
        Args:
            index_name (str): The name of the index to ingest the document into.
            document_id (str): A unique identifier for the document being ingested.
            filename (str): The original filename of the document being ingested.
            content (bytes): The raw content of the document being ingested.
            metadata (Optional[dict]): Optional custom metadata to associate with the document.
        Returns:            IngestDocumentJob: An object representing the ingest job that was created to process the document.                              
        This includes information about the job status, progress, and any errors that may have occurred."""
        
        if self.logger:
            self.logger.debug(f"Ingesting document: {request.document_id} from index: {request.index_name}")


        proto_request = document_service_pb2.IngestDocumentRequest(index_name=request.index_name, 
                                                             document_id=request.document_id,
                                                             filename=request.filename, 
                                                             content=request.content,
                                                             content_type=request.content_type,
                                                             metadata=request.metadata,
                                                             embeddings_client=request.embeddings_client,
                                                             batch_size=request.batch_size,
                                                             embeddings_model=request.embeddings_model,
                                                             chunk_strategy=request.chunk_strategy)
        resp = self._stub.IngestDocument(proto_request, metadata=self.route_metadata)
        return self.proto_to_ingest_job(resp)
    
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