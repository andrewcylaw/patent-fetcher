from datetime import datetime

import pytest
from pydantic import ValidationError

from patent_fetcher.clients.patent_client import PatentClient
from patent_fetcher.constants import OUTPUT_CLIENT, Output
from patent_fetcher.models.api import PatentsApiRequest, PatentsApiRequestPage
from patent_fetcher.models.patent_client import PatentsClientRequest


@pytest.fixture(scope="function")
def valid_patent_client() -> dict:
    # Default valid clients mock parameters
    return {
        "start_date": "2024-01-01",
        "end_date": "2024-01-02",
        "page_size": 1000,
        "local_output": False,
    }

#
# def test_integration(valid_patent_client):
#     client = PatentClient()
#     client_request = PatentsClientRequest(
#         api_request=PatentsApiRequest(
#             grant_from_date=datetime.strptime("2024-01-01", "%Y-%m-%d"),
#             grant_to_date=datetime.strptime("2024-01-02", "%Y-%m-%d"),
#             pagination=PatentsApiRequestPage(page=2, page_size=20)
#         ),
#         output_client=OUTPUT_CLIENT.get(Output.SQLITE),
#         num_pages=3,
#         start_page=5
#     )
#     client.fetch_patents(client_request)