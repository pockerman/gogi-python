import os
from typing import Optional
from gogi.clients.documents_client import DocumentsClient
from gogi.clients.indexes_client import IndexesClient

class Gogi:
    """
        Main platform SDK entry point.

        Provides lazy-initialized access to all platform services.
        Services are initialized on first access to avoid unnecessary
        network connections.

        Example:
            gogi = Gogi()
            session = gogi.sessions.get_or_create(user_id="user-123")
            response = gogi.models.chat(model="gpt-4o", query="Hello")
    """

    def __init__(self, gateway_url: str = "localhost:50051", logger=None):
        if gateway_url:
            self.gateway_url = gateway_url
        else:
            self.gateway_url = os.getenv("GENAI_GATEWAY_URL", "localhost:50051")
        self.logger = logger

        # Lazy initialization - clients created on first access
        self._sessions = None
        self._models = None
        self._indexes: Optional[IndexesClient] = None
        self._documents: Optional[DocumentsClient] = None
        self._guardrails = None
        self._tools = None
        self._evaluation = None
        self._workflows = None

    @property
    def documents(self) -> DocumentsClient:
        if not self._documents:
            self._documents = DocumentsClient(platform=self, logger=self.logger)
        return self._documents

    @property
    def indexes(self) -> IndexesClient:
        if not self._indexes:
            self._indexes = IndexesClient(platform=self, logger=self.logger)
        return self._indexes