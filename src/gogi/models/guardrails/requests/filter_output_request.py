from pydantic import BaseModel


class FilterOutputRequest(BaseModel):
    content: str = ""
    # built-in filters, which redact what they find: pii_redaction
    filters: list[str] = []
    context: dict[str, str] = {}
    # the output policies to apply
    policy_names: list[str] = []
    # applies the output policies of the application, and those of every application
    application_id: str = ""
