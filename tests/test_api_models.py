from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from patent_fetcher.models.api import (
    PatentsApiResponsePage,
    Patent,
    HealthApiResponse,
    PatentsApiRequestPage,
    PatentsApiRequest,
    PatentsApiResponse
)
from patent_fetcher.settings import cli_settings


def test_patent_model_valid():
    Patent(
        patent_number="number",
        title="title",
        grant_date=date.today(),
        description="description",
        abstract="abstract",
        claims=["claims"],
        assignees=["assignees"],
        inventors=["inventors"],
    )

# minimal assertion that model instantiation works
def test_health_api_response_valid():
    response = HealthApiResponse(service="health-check-service", status="ok")
    assert response.status == "ok"

def test_patents_api_response_page_valid():
    response = PatentsApiResponsePage(page=1, page_size=1000, total_pages=1, total_items=1)
    assert response.page == 1

@pytest.mark.parametrize(
    "page, page_size, total_pages, total_items", [
        (-1, 0, 0, 0),
        (0, -1, 0, 0),
        (0, 0, -1, 0),
        (0, 0, 0, -1),
    ])
def test_patents_api_response_invalid(page, page_size, total_pages, total_items):
    with pytest.raises(ValidationError):
        PatentsApiResponsePage(page=page, page_size=page_size, total_pages=total_pages, total_items=total_items)

def test_patents_api_response_valid():
    response = PatentsApiResponse(
        patents=[],
        pagination=PatentsApiResponsePage(page=1, page_size=10, total_pages=1, total_items=0)
    )
    assert response.pagination.page == 1

def test_patents_api_request_page_valid():
    # Test that defaults are set properly
    # Note that a productionized setup would have test environment specific .env files, etc
    request = PatentsApiRequestPage()
    assert request.page == 1
    assert request.page_size == cli_settings.max_page_size

@pytest.mark.parametrize("page, page_size", [(-1, 0), (1, 0)])
def test_patents_api_request_page_invalid_pages(page, page_size):
    with pytest.raises(ValidationError):
        PatentsApiRequestPage(page=page, page_size=page_size)

def test_patents_api_request_valid():
    PatentsApiRequest(
        grant_from_date=date.today() - timedelta(days=1),
        grant_to_date=date.today(),
        pagination=PatentsApiRequestPage()
    )

def test_patents_api_request_invalid_dates():
    with pytest.raises(ValidationError):
        PatentsApiRequest(
            grant_from_date=date.today(),
            grant_to_date=date.today() - timedelta(days=1),
            pagination=PatentsApiRequestPage()
        )
