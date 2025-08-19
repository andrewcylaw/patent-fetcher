import logging
import sys
from typing import ClassVar
from urllib.parse import urljoin

import requests
from requests import HTTPError

from patent_fetcher.clients.output.base_client import OutputClient
from patent_fetcher.models.api import HealthApiResponse, PatentsApiRequest, PatentsApiResponse, Patent
from patent_fetcher.models.output_client import OutputClientResponse
from patent_fetcher.models.patent_client import PatentsClientRequest, PatentsClientResponse
from patent_fetcher.settings import cli_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PatentClient:
    HEALTH_PATH: ClassVar[str] = "/health"
    PATENTS_PATH: ClassVar[str] = "/patents"

    @staticmethod
    def _request(method: str, endpoint: str, payload: str | None = None) -> dict | list:
        """
        Makes an HTTP request against the given endpoint using the given method and an optional payload.

        :param method: HTTP method (GET/POST/etc)
        :param endpoint: endpoint to be appended to base url
        :param payload: optional json payload
        :return: the json response as a string
        :raises: HTTPError if anything goes wrong
        """
        full_url = urljoin(str(cli_settings.api_url), endpoint)
        headers = {
            "Authorization": f"Bearer {cli_settings.api_token.get_secret_value()}",
            "Content-Type": "application/json",
        }
        try:
            logger.info(f"Attempting to send request to {full_url} with payload={payload}")
            response = requests.request(method, url=full_url, headers=headers, data=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Conscious decision here to just catch-and-reraise a generic HTTPError,
            # in production, better retry/error handling should happen for specific cases (eg failure notification)
            logger.error(f"Exception when trying to {method} on {endpoint} with payload {payload} - {e}")
            raise HTTPError(e)

    def check_health(self) -> HealthApiResponse:
        """
        Performs a health ping before the start of a new patent fetch request

        :return: HealthResponse containing health check information
        :raises: HTTPError if health check fails
        """
        raw_response = self._request(method="GET", endpoint=self.HEALTH_PATH)
        health_response = HealthApiResponse.model_validate(raw_response)
        logger.info(f"Health check success - service={health_response.service} status={health_response.status}")
        return health_response

    def fetch_patents(self, request: PatentsClientRequest) -> PatentsClientResponse:
        """
        Attempts to fetch patents from upstream using the configs defined in the environment

        :return: PatentsClientResponse
        :raises: ValueError if anything goes wrong
        """
        logger.info(f"Beginning patent fetch with payload {request.model_dump_json()}")
        health_status = self.check_health()
        if health_status.status != "healthy":
            raise ValueError(f"Health check failed with status {health_status}")

        cur_page = request.start_page
        buffer, output_info = [], []
        num_patents_fetched, num_pages_fetched = 0, 0
        payload = request.api_request
        try:
            # First request fetches metadata
            logger.info(f"Fetching initial page {cur_page}")
            first_response = self._fetch_patent_page(payload)
            total_pages = first_response.pagination.total_pages
            total_items = first_response.pagination.total_items

            if total_pages == 0 or total_items == 0:
                logger.info(f"No patents found for {payload.model_dump_json()}")
                return PatentsClientResponse()

            buffer.extend(first_response.patents)
            num_patents_fetched += len(first_response.patents)
            logger.info(f"Successfully fetched initial page {cur_page} (total_pages={total_pages}, total_items={total_items})")
            logger.info(f"Successfully fetched a total of {len(first_response.patents)} patents from page {cur_page}")

            num_pages_fetched += 1
            cur_page += 1

            while (not request.num_pages and cur_page <= total_pages) or (request.num_pages is not None and num_pages_fetched < request.num_pages):
                logger.info(f"Attempting to fetch page {cur_page}")
                payload.pagination.page = cur_page
                patents_resp = self._fetch_patent_page(payload)
                buffer.extend(patents_resp.patents)

                num_patents_fetched += len(patents_resp.patents)
                num_pages_fetched += 1

                logger.info(f"Successfully fetched a total of {len(patents_resp.patents)} patents from page {cur_page}")
                if len(buffer) >= cli_settings.buffer_size:
                    output_info.append(self._flush_patent_buffer(request.output_client, buffer))
                    buffer.clear()

                cur_page += 1

            # Flush after final iteration
            output_info.append(self._flush_patent_buffer(request.output_client, buffer))
            return PatentsClientResponse(
                total_items_found=total_items,
                total_items_fetched=num_patents_fetched,
                total_pages_fetched=num_pages_fetched,
                total_items_outputted=sum(output.num_items_outputted for output in output_info),
                output_info=output_info
            )
        except Exception as e:
            # On fetch failure, attempt to flush remaining buffer and reraise the exception
            logger.error(f"Exception occurred when attempting to fetch page {cur_page} with payload {payload.model_dump_json()} - {e}")
            if buffer:
                self._flush_patent_buffer(request.output_client, buffer)
            raise ValueError(e)

    def _fetch_patent_page(self, payload: PatentsApiRequest) -> PatentsApiResponse:
        """
        Fetches a single page of patents
        :return: the raw response from the api as a PatentsApiResponse object
        """
        patents_response = self._request(
            method="POST",
            endpoint=self.PATENTS_PATH,
            payload=payload.model_dump_json(),
        )
        return PatentsApiResponse.model_validate(patents_response)

    @staticmethod
    def _flush_patent_buffer(output_client_cls: type[OutputClient] | None, patents: list[Patent]) -> OutputClientResponse | None:
        """
        Attempts to dump the given buffer of patents either to local disk or to a database

        :raises: ValueError if the clients fails to flush the buffer for any reason
        """
        if not patents:
            logger.info(f"No patents to flush")
            return OutputClientResponse()

        if not output_client_cls:
            logger.info(f"No output client provided, skipping flush of {len(patents)} items")
            return OutputClientResponse(num_items_outputted=len(patents))

        logger.info(f"Attempting to flush {len(patents)} patents using {output_client_cls.__name__}")
        output_client = output_client_cls()
        client_response = output_client.output_patents(patents)
        logger.info(f"Successfully flushed {client_response.num_items_outputted} patents "
                    f"using {output_client_cls.__name__} - {client_response}")
        return client_response