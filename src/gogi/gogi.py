import os
from typing import Optional
from gogi.clients.documents_client import DocumentsClient
from gogi.clients.indexes_client import IndexesClient
from gogi.clients.llm_models_client import LLMModelsClient
from gogi.clients.prompts_client import PromptsClient
from gogi.clients.llm_sessions_client import LLMSessionsClient

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
        self._llm_sessions: Optional[LLMSessionsClient] = None
        self._indexes: Optional[IndexesClient] = None
        self._documents: Optional[DocumentsClient] = None
        self._llm_models: Optional[LLMModelsClient] = None
        self._prompts: Optional[PromptsClient] = None
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
    
    @property
    def llm_clients(self) -> LLMModelsClient:
        if not self._llm_models:
            self._llm_models = LLMModelsClient(platform=self, logger=self.logger)
        return self._llm_models
    
    @property
    def llm_session(self) -> LLMSessionsClient:
        if not self._llm_sessions:
                 self._llm_sessions = LLMSessionsClient(platform=self, logger=self.logger)
        return self._llm_sessions

    
    @property
    def prompts(self) -> PromptsClient:
        if not self._prompts:
            self._prompts = PromptsClient(platform=self, logger=self.logger)
        return self._prompts
    
