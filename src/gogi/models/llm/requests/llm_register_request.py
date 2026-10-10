from pydantic import BaseModel

from gogi.models.llm.llm_model_info import LLMModelInfo


class LLMRegisterRequest(BaseModel):
    info: LLMModelInfo
    endpoint: str
    health_check: str
    adapter_type: str
    # names a credential held by the platform's credential store, e.g. "ml-inference-prod";
    # the secret itself never appears in the registration. Empty if the endpoint needs none
    credential_ref: str = ""
