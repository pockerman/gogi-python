from typing import List
from loguru import logger


from gogi.clients.models.index_config import IndexConfig
from gogi.clients.models.index import Index
from gogi.clients.base_client import BaseClient
from gogi.v1.data import index_service_pb2
from gogi.v1.data import index_service_pb2_grpc



class IndexesClient(BaseClient):


    @staticmethod
    def proto_to_index_config(proto_config: index_service_pb2.IndexConfig) -> IndexConfig:
        return IndexConfig(
            name=proto_config.name,
            embedding_model=proto_config.embedding_model,
            embedding_dimensions=proto_config.embedding_dimensions,
            chunking_strategy=proto_config.chunking_strategy,
            chunk_size=proto_config.chunk_size,
            chunk_overlap=proto_config.chunk_overlap,
            metadata_schema=dict(proto_config.metadata_schema)
        )

    @staticmethod
    def proto_to_index(resp) -> Index:
        return Index(
            name=resp.name,
            config=IndexesClient.proto_to_index_config(resp.config),
            owner=resp.owner,
            document_count=resp.document_count,
            total_chunks=resp.total_chunks,
            created_at=resp.created_at,
            last_ingested_at=resp.last_ingested_at
        )



    def __init__(self, platform, logger=None):
        super().__init__(platform=platform, service_name="indexes", logger=logger)
        self._stub = index_service_pb2_grpc.IndexServiceStub(self._channel)

    def create_index(self, owner_name: str, config: IndexConfig) -> Index:

        if self.logger:
            self.logger.debug(f"Creating index with config: {config}")


        index_config_proto = index_service_pb2.IndexConfig(
            name=config.name,
            embedding_model=config.embedding_model,
            embedding_dimensions=config.embedding_dimensions,
            chunking_strategy=config.chunking_strategy,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            metadata_schema=config.metadata_schema
        )

        request = index_service_pb2.CreateIndexRequest(owner=owner_name, 
                                                       config=index_config_proto)
        resp = self._stub.CreateIndex(request, metadata=self.route_metadata)
        return self.proto_to_index(resp)


    def list_indexes(self, owner_name: str) -> List[Index]:
        if self.logger:
            self.logger.debug(f"Listing indexes for owner: {owner_name}")

        request = index_service_pb2.ListIndexesRequest()
        resp = self._stub.ListIndexes(request, metadata=self.route_metadata)
        return [self.proto_to_index(index) for index in resp.indexes]

    def get_index(self, index_name: str) -> Index:
        if self.logger:
            self.logger.debug(f"Getting index: {index_name}")
            
        request = index_service_pb2.GetIndexRequest(index_name=index_name)
        resp = self._stub.GetIndex(request, metadata=self.route_metadata)
        return self.proto_to_index(resp)

    def delete_index(self, index_name: str) -> bool:
        if self.logger:
            self.logger.debug(f"Deleting index: {index_name}")
        request = index_service_pb2.DeleteIndexRequest(index_name=index_name)
        resp = self._stub.DeleteIndex(request, metadata=self.route_metadata)
        return resp.success
