import json
from typing import Self

from pydantic import BaseModel


class LLMResponseFormat(BaseModel):
    """Asks the model to answer with a JSON object: "json_object" for any object, or "json_schema" for one that
    matches ``response_schema_json``. The response's content is then the object, as JSON."""

    response_type: str
    response_schema_json: str = ""

    @classmethod
    def json_schema(cls, model: type[BaseModel]) -> Self:
        """the format of an answer that is a ``model``, which the answer can be validated into"""
        return cls(response_type="json_schema", response_schema_json=json.dumps(model.model_json_schema()))

    @classmethod
    def json_object(cls) -> Self:
        return cls(response_type="json_object")


# the class's original, misspelled name
LLMRespnseFormat = LLMResponseFormat
