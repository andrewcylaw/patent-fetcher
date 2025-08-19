from datetime import date, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from urllib3.exceptions import HTTPError

from patent_fetcher.clients.output.local import LocalOutputClient
from patent_fetcher.clients.patent_client import PatentClient
from patent_fetcher.models.api import (
    HealthApiResponse,
    Patent,
    PatentsApiRequest,
    PatentsApiRequestPage,
    PatentsApiResponse,
    PatentsApiResponsePage
)
from patent_fetcher.models.output_client import OutputClientResponse
from patent_fetcher.models.patent_client import PatentsClientRequest

"""
Tests for the PatentClient:
- Monkey patching the client's methods is done for demo purposes
- A more production-ready approach would be to DI an HTTP client, and then change out the implementation for these tests
  to return mock data
  
"""


# Quick and dirty patches to stub requests.request() behaviours
def _health_check_ok(**_) -> HealthApiResponse:
    return HealthApiResponse(status="healthy", service="check-health-test")

def _raise_http_error(self: Any | None = None, **_) -> None:
    raise HTTPError("test error")

def _mock_patents_api(total_pages: int, total_items: int, num_mocks: int | None = 1, ) -> PatentsApiResponse:
    # Generates a response mimicking what the api endpoint would pass
    patents = []
    for i in range(num_mocks):
        mock_patent = Patent(
            patent_number=f"patent_number_{i}",
            title="title",
            grant_date=date.today(),
            abstract="abstract",
            claims=["claims"],
            assignees=["assignees"],
            inventors=["inventors"],
            description="description"
        )
        patents.append(mock_patent)
    # pagination assumed correct from api, tests will modify the value as needed
    return PatentsApiResponse(
        patents=patents,
        pagination=PatentsApiResponsePage(
            page=0,
            page_size=0,
            total_pages=total_pages,
            total_items=total_items,
        )
    )


@pytest.fixture
def patents_api_request() -> PatentsApiRequest:
    # Sample valid api request
    return PatentsApiRequest(
        grant_from_date=date.today(),
        grant_to_date=date.today() + timedelta(days=1),
        pagination=PatentsApiRequestPage(
            page=1, page_size=100
        )
    )

def test_check_health_valid():
    client = PatentClient()
    client._request = _health_check_ok
    response = client.check_health()
    assert response.status == "healthy"
    assert response.service == "check-health-test"

def test_check_health_raise_http_error():
    with pytest.raises(HTTPError):
        client = PatentClient()
        client._request = _raise_http_error
        client.check_health()

def test_flush_buffer_no_client():
    mock_api_response = _mock_patents_api(num_mocks=1, total_pages=1, total_items=1)
    response = PatentClient()._flush_patent_buffer(None, mock_api_response.patents)
    assert response.num_items_outputted == 1

def test_flush_buffer_no_patents():
    response = PatentClient()._flush_patent_buffer(LocalOutputClient, [])
    assert response.num_items_outputted == 0

def test_fetch_patents_all_pages(patents_api_request):
    client = PatentClient()
    client.check_health = _health_check_ok

    def _fake_fetch_patent_page(api_request):
        if api_request.pagination.page == 1:
            return _mock_patents_api(num_mocks=2, total_items=5, total_pages=3)
        elif api_request.pagination.page == 2:
            return _mock_patents_api(num_mocks=2, total_items=5, total_pages=3)
        else:
            return _mock_patents_api(num_mocks=1, total_items=5, total_pages=3)

    client._fetch_patent_page = _fake_fetch_patent_page
    response = client.fetch_patents(
        PatentsClientRequest(api_request=patents_api_request, output_client=None)
    )

    assert response.total_items_found == 5
    assert response.total_items_fetched == 5
    assert response.total_pages_fetched == 3
    assert response.total_items_outputted == 5
    assert response.output_info == [OutputClientResponse(num_items_outputted=5, output_info={})]

def test_fetch_patents_failed_health_check(patents_api_request):
    client = PatentClient()
    client.check_health = lambda: HealthApiResponse(status="bad", service="check-health-test")
    with pytest.raises(ValueError):
        client.fetch_patents(PatentsClientRequest(api_request=patents_api_request))

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_start_page_all_pages(patents_api_request):
    # Given a start page and no specified page count, fetch all pages
    # Tests start_page != 1, num_pages=None
    pass

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_no_items_all_pages(patents_api_request):
    # Test where the api returns no patents for our request
    pass

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_start_page_num_pages():
    # Given a start page and specified number of pages to fetch
    # Tests num_pages is not None
    pass

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_buffer_flush():
    # Test that we flush our buffer as expected
    pass

def test_fetch_patents_flush_on_error(patents_api_request):
    # Test that we correctly flush our buffer on http error
    mock_output = MagicMock()

    def _fake_fetch_patent_page(api_request):
        if api_request.pagination.page == 1:
            return _mock_patents_api(num_mocks=2, total_items=5, total_pages=3)
        raise HTTPError("error")

    client = PatentClient()
    client.check_health = _health_check_ok
    client._fetch_patent_page = _fake_fetch_patent_page
    client._flush_patent_buffer = mock_output

    with pytest.raises(ValueError):
        client.fetch_patents(PatentsClientRequest(api_request=patents_api_request))

    mock_output.assert_called_once()

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_flush_buffer_valid():
    pass
