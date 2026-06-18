from typing import List
from loguru import logger



from gogi.clients.models.gogi_index import GogiIndex
from gogi.clients.base_client import BaseClient
from gogi.v1.data import index_service_pb2
from gogi.v1.data import index_service_pb2_grpc



class IndexesClient(BaseClient):


    @staticmethod
    def proto_to_index(resp) -> GogiIndex:
        return GogiIndex(
            index_id=resp.id,
            index_name=resp.index_name,
            owner=resp.owner,
            created_at=resp.created_at,
            last_updated_at=resp.last_updated_at
        )


    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="indexes", logger=logger)
        self._stub = index_service_pb2_grpc.IndexServiceStub(self._channel)

    def create_index(self, index_name: str, owner_name: str) -> GogiIndex:

        if self.logger:
            self.logger.debug(f"Creating index {index_name} with name: {owner_name}")

        request = index_service_pb2.CreateIndexRequest(owner=owner_name, 
                                                       index_name=index_name)
        resp = self._stub.CreateIndex(request, metadata=self.route_metadata)
        return self.proto_to_index(resp)


    def list_owner_indexes(self, owner_name: str) -> List[GogiIndex]:
        if self.logger:
            self.logger.debug(f"Listing indexes for owner: {owner_name}")

        request = index_service_pb2.ListIndexesRequest(owner_name=owner_name)
        resp = self._stub.ListIndexes(request, metadata=self.route_metadata)
        return [self.proto_to_index(index) for index in resp.indexes]
    
    def get_index_by_name(self, index_name: str) -> GogiIndex:
        if self.logger:
            self.logger.debug(
                f"Getting index (name={index_name})",)

        request = index_service_pb2.GetIndexByNameRequest(index_name=index_name)
        resp = self._stub.GetIndexByName(request, metadata=self.route_metadata)
        return self.proto_to_index(resp)
    
    def get_index_by_id(self, index_id: str) -> GogiIndex:
        if self.logger:
            self.logger.debug(
            f"Getting index (id={index_id})")
        request = index_service_pb2.GetIndexByIdRequest(index_id=index_id)
        resp = self._stub.GetIndexById(request, metadata=self.route_metadata)
        return self.proto_to_index(resp)


    def get_index(self, *, index_name: str | None = None, index_id: str | None = None) -> GogiIndex:

        if (index_id is None) == (index_name is None):
            raise ValueError("Specify exactly one of index_id or index_name")

        if index_name:
            return self.get_index_by_name(index_name=index_name)
        
        return self.get_index_by_id(index_id=index_id)


    def delete_index_by_name(self, index_name: str) -> bool:
        if self.logger:
            self.logger.debug(f"Deleting index: {index_name}")
        request = index_service_pb2.DeleteIndexByNameRequest(index_name=index_name)
        resp = self._stub.DeleteIndexByName(request, metadata=self.route_metadata)
        return resp.success
    
    def delete_index_by_id(self, index_id: str) -> bool:
        if self.logger:
            self.logger.debug(f"Deleting index: {index_id}")
        request = index_service_pb2.DeleteIndexByIdRequest(index_id=index_id)
        resp = self._stub.DeleteIndexById(request, metadata=self.route_metadata)
        return resp.success
    
    def delete_index(self, *, index_name: str | None, index_id: str | None = None) -> bool:
        if (index_id is None) == (index_name is None):
            raise ValueError("Specify exactly one of index_id or index_name")
        
        if index_name:
            return self.delete_index_by_name(index_name=index_name)
        
        return self.delete_index_by_id(index_id=index_id)

    
    def delete_owner_indexes(self, owner: str) -> bool:
        if self.logger:
            self.logger.debug(f"Deleting index: {owner}")
        request = index_service_pb2.DeleteOwnerIndexesRequest(owner_name=owner)
        resp = self._stub.DeleteOwnerIndexes(request, metadata=self.route_metadata)
        return resp.success
