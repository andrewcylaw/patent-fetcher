from typing import Annotated

from pydantic import Field, BaseModel, BeforeValidator, field_serializer

from patent_fetcher.clients.output.base_client import OutputClient
from patent_fetcher.clients.output.local import LocalOutputClient
from patent_fetcher.models.api import PatentsApiRequest
from patent_fetcher.models.output_client import OutputClientResponse
from patent_fetcher.models.utils import default_if_none


class PatentsClientRequest(BaseModel):
    """
    Root model representing the patent client's fetch payload.
    Contains additional options that are local to program execution and not the api
    """
    api_request: PatentsApiRequest
    output_client: type[OutputClient] | None = LocalOutputClient
    num_pages: int | None = None
    start_page: Annotated[int, BeforeValidator(default_if_none)] = Field(default=1, ge=1)

    @field_serializer("output_client")
    def serialize_output(self, output_client: type[OutputClient]) -> str:
        return output_client.__name__ if output_client else ""


class PatentsClientResponse(BaseModel):
    """
    Root models representing the expected patent clients response containing metrics and output information

    Fetched/outputted metrics separated as not every item is guaranteed to be written out successfully
    """
    total_items_found: Annotated[int, BeforeValidator(default_if_none)] = Field(default=0)
    total_items_fetched: int = 0
    total_pages_fetched: int = 0
    total_items_outputted: Annotated[int, BeforeValidator(default_if_none)] = Field(default=0)
    output_info: list[OutputClientResponse] | None = Field(default_factory=list)
