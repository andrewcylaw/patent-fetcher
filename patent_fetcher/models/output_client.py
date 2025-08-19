from typing import Any, Annotated

from pydantic import BaseModel, BeforeValidator
from pydantic import Field

from patent_fetcher.models.utils import default_if_none


class OutputClientResponse(BaseModel):
    """
    Root models representing any information or messages created by an output clients.

    (These should be defined more rigourously, but I am using a simple dict for now
    """
    num_items_outputted: Annotated[int, BeforeValidator(default_if_none)] = Field(default=0)
    output_info: dict[str, Any] | None = Field(default_factory=dict)
