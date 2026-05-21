from typing import List

from gogi.clients.models.document_metadata import DocumentMetadata
from gogi.clients.base_client import BaseClient
from gogi.v1.data import document_service_pb2
from gogi.v1.data import document_service_pb2_grpc


class DocumentsClient(BaseClient):
    def __init__(self, platform):
        super().__init__(platform=platform, service_name="documents")
        self._stub = document_service_pb2_grpc.DocumentServerStub(self._channel)

    def list_documents(self, index_name: str) -> List[DocumentMetadata]:
        request = document_service_pb2.ListDocumentsRequest(index_name=index_name)
        resp = self._stub.ListDocuments(request, metadata=self.route_metadata)
        return [self._proto_to_doc_meta(d) for d in resp.documents]

    def get_document(self, index_name: str, document_id: str) -> DocumentMetadata:
        request = document_service_pb2.GetDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.GetDocument(request, metadata=self.route_metadata)
        return self._proto_to_doc_meta(resp)

    def delete_document(self, index_name: str, document_id: str) -> bool:
        request = document_service_pb2.DeleteDocumentRequest(index_name=index_name, document_id=document_id)
        resp = self._stub.DeleteDocument(request, metadata=self.route_metadata)
        return resp.success
