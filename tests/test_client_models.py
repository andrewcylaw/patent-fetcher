from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from patent_fetcher.clients.output.local import LocalOutputClient
from patent_fetcher.models.api import (
    PatentsApiRequestPage,
    PatentsApiRequest
)
from patent_fetcher.models.output_client import OutputClientResponse
from patent_fetcher.models.patent_client import PatentsClientRequest, PatentsClientResponse

"""
General testing idea is:
 - Sanity checks for all models that they instantiate properly and defaults are set
 - For each model, check for edge cases of note
 
Some of the repeated cases are intentionally left blank for this demo 
"""

@pytest.fixture(scope='module')
def valid_patents_api_request():
    return PatentsApiRequest(
        grant_from_date=date.today() - timedelta(days=1),
        grant_to_date=date.today(),
        pagination=PatentsApiRequestPage()
    )


def test_output_client_response_valid():
    response = OutputClientResponse()
    assert response.num_items_outputted == 0
    assert response.output_info == dict()

def test_patents_client_request_valid(valid_patents_api_request):
    client = PatentsClientRequest(api_request=valid_patents_api_request)
    assert client.output_client == LocalOutputClient
    assert client.num_pages is None
    assert client.start_page == 1

def test_patents_client_request_serializer(valid_patents_api_request):
    client = PatentsClientRequest(api_request=valid_patents_api_request)
    assert client.model_dump().get("output_client") == "LocalOutputClient"

    client = PatentsClientRequest(api_request=valid_patents_api_request, output_client=None)
    assert not client.model_dump().get("output_client")

def test_patents_client_request_invalid(valid_patents_api_request):
    with pytest.raises(ValidationError):
        PatentsClientRequest(api_request=valid_patents_api_request, start_page=-1)

def test_patents_client_response_valid():
    # Test defaults
    response = PatentsClientResponse()
    assert response.total_items_found == 0
    assert response.total_items_fetched == 0
    assert response.total_pages_fetched == 0
    assert response.total_items_outputted == 0
    assert response.output_info == list()

def test_patents_client_response_mutable():
    # Test that our default factories are not shared
    response1 = PatentsClientResponse()
    response2 = PatentsClientResponse()
    assert response1.output_info is not response2.output_info
