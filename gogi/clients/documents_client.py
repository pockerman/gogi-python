import grpc
from typing import List

from gogi.clients.models.document_metadata import DocumentMetadata
from gogi.clients.base_client import BaseClient


class DocumentsClient(BaseClient):
    def __init__(self, platform):
        super().__init__(platform=platform, service_name="documents")

    def list_documents(self, index_name: str) -> List[DocumentMetadata]:
        request = data_pb2.ListDocumentsRequest(index_name=index_name)
        resp = self._stub.ListDocuments(request, metadata=self._metadata)
        return [self._proto_to_doc_meta(d) for d in resp.documents]

    def get_document(self, index_name: str, document_id: str) -> DocumentMetadata:
        request = data_pb2.GetDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.GetDocument(request, metadata=self._metadata)
        return self._proto_to_doc_meta(resp)

    def delete_document(self, index_name: str, document_id: str) -> bool:
        request = data_pb2.DeleteDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.DeleteDocument(request, metadata=self._metadata)
        return resp.success
