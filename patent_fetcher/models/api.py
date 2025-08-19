from datetime import date
from typing import Self, Annotated

from pydantic import BaseModel, BeforeValidator
from pydantic import Field, model_validator

from patent_fetcher.models.utils import default_if_none
from patent_fetcher.settings import cli_settings


class Patent(BaseModel):
    patent_number: str
    title: str
    grant_date: date
    abstract: str
    claims: list[str]
    assignees: list[str]
    inventors: list[str]
    description: str


class HealthApiResponse(BaseModel):
    """
    Root models representing the patents health check API response.

    For simplicity, I'm directly surfacing the API's response back to the clients, but if we have more transformations
    or usage scenarios, then I would wrap this in something like a "ClientHealthResponse"

    FIXME these should probably be enums, but I don't know what other values these could be
    """
    status: str
    service: str


class PatentsApiResponsePage(BaseModel):
    """
    Pagination models representing the patents fetcher API response
    """
    page: int = Field(ge=0)
    page_size: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    total_items: int = Field(ge=0)


class PatentsApiResponse(BaseModel):
    """
    Root models representing the patents fetcher API response
    """
    patents: list[Patent]
    pagination: PatentsApiResponsePage


class PatentsApiRequestPage(BaseModel):
    """
    Model representing the pagination response for the patents fetcher API.

    The given page size to fetch at a time cannot be larger than the in-memory buffer size
    """
    page: Annotated[int, BeforeValidator(default_if_none)] = Field(default=1, ge=1)
    page_size: Annotated[int, BeforeValidator(default_if_none)] = Field(default=cli_settings.max_page_size, ge=1, le=cli_settings.max_page_size)


class PatentsApiRequest(BaseModel):
    """
    Root models representing the payload required to interact with the patents fetcher API
    """
    grant_from_date: date
    grant_to_date: date
    pagination: PatentsApiRequestPage

    @model_validator(mode="after")
    def check_valid_dates(self) -> Self:
        if self.grant_from_date >= self.grant_to_date:
            raise ValueError(f"Grant to date ({self.grant_to_date} must be greater than grant from date ({self.grant_from_date}))")
        return self
