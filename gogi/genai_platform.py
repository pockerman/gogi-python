from .model_client import ModelClient
from .base_client import BaseClient

class GenAIPlatform:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self._sessions = None    
        self._models = None    
        self._data = None    

    @property
    def models(self) -> BaseClient:
        if not self._models:
            self._models = ModelClient(host=self.gateway_url)

        return self._models

    