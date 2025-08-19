import json
import logging
import sys
from datetime import datetime

import click

from patent_fetcher.clients.patent_client import PatentClient
from patent_fetcher.constants import Output, OUTPUT_CLIENT
from patent_fetcher.models.api import PatentsApiRequest, PatentsApiRequestPage, HealthApiResponse
from patent_fetcher.models.patent_client import PatentsClientResponse, PatentsClientRequest
from patent_fetcher.settings import cli_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command()
@click.argument("start_date", type=click.DateTime())
@click.argument("end_date", type=click.DateTime())
def patent_fetcher(start_date: datetime, end_date: datetime) -> PatentsClientResponse:
    """
    This was a conscious decision to add an extra function so that the example from the readme can be executed as-is,
    otherwise - this is just a passthrough to the main CLI

    eg patent_fetcher 2001-04-25 2001-05-25

    :return: PatentsClientResponse containing information about the fetched patents
    """
    logger.info(f"Beginning patents fetching using {json.dumps(locals(), default=str)}")
    return fetch_patents.callback(start_date, end_date)


@click.command()
@click.argument("start_date", type=click.DateTime())
@click.argument("end_date", type=click.DateTime())
@click.option(
    "--start_page",
    type=int,
    help="Optional - specifies the page to start fetching from if provided. If omitted, starts from page 1"
)
@click.option(
    "--num_pages",
    type=int,
    help="Optional - specifies the number of pages to fetch. If omitted, fetches all pages"
)
@click.option(
    "--page_size",
    type=int,
    help=f"Optional - number of items to fetch per page, defaults to {cli_settings.max_page_size}")
@click.option(
    "--output",
    type=click.Choice(Output, case_sensitive=False),
    help="Optional - specifies output location, defaults to none"
)
def fetch_patents(
        start_date: datetime,
        end_date: datetime,
        start_page: int | None = 1,
        num_pages: int | None = None,
        page_size: int | None = None,
        output: Output | None = None
) -> PatentsClientResponse:
    """
    Fetches patents from the patent API between START_DATE and END_DATE and outputs them to OUTPUT.
    Optionally, NUM_PAGES can be fetched of PAGE_SIZE each, starting from a specific START_PAGE.

    :return: PatentsClientResponse containing information about the fetched patents
    """
    logger.info(f"Beginning patents fetching using {json.dumps(locals(), default=str)}")
    client_request = PatentsClientRequest(
        api_request=PatentsApiRequest(
            grant_from_date=start_date.date(),
            grant_to_date=end_date.date(),
            pagination=PatentsApiRequestPage(page=start_page, page_size=page_size)
        ),
        output_client=OUTPUT_CLIENT.get(output),
        num_pages=num_pages,
        start_page=start_page
    )
    client = PatentClient()
    return client.fetch_patents(client_request)


@click.command()
def check_health() -> HealthApiResponse:
    """
    Performs a health check against the patent API.
    """
    logger.info(f"Beginning patents api health check")
    return PatentClient().check_health()


@click.group()
def cli():
    pass


cli.add_command(fetch_patents)
cli.add_command(check_health)
