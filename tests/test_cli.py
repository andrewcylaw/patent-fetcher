from unittest.mock import patch

import pytest
from click.testing import CliRunner

from patent_fetcher.cli import fetch_patents, check_health


@patch("patent_fetcher.cli.PatentsClientRequest", autospec=True)
@patch("patent_fetcher.cli.PatentClient", autospec=True)
def test_fetch_patents_valid_default(mock_client, mock_request):
    result = CliRunner().invoke(fetch_patents, ["2024-01-01", "2024-01-02"])
    mock_request.assert_called_once()
    mock_client.assert_called_once()
    mock_client.return_value.fetch_patents.assert_called_once()

    assert result.exit_code == 0

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_valid():
    pass

def test_fetch_patents_invalid_date():
    runner = CliRunner()

    # invalid date
    result = runner.invoke(fetch_patents, ["bad date"])
    assert result.exit_code != 0

    # missing 2nd arg
    result = runner.invoke(fetch_patents, ["2024-01-01"])
    assert result.exit_code != 0

@pytest.mark.skip(reason="Full test coverage would check all inputs / edge cases, consciously skipped for brevity")
def test_fetch_patents_invalid_page():
    # test edge cases for dates - such as bad formatting, start/end date overlap, etc
    pass

@patch("patent_fetcher.cli.PatentClient", autospec=True)
def test_check_health(mock_client):
    result = CliRunner().invoke(check_health)
    mock_client.assert_called_once()
    mock_client.return_value.check_health.assert_called_once()

    assert result.exit_code == 0
