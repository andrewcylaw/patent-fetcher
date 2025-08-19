import gzip
import json
import logging
from datetime import datetime

from patent_fetcher.clients.output.base_client import OutputClient
from patent_fetcher.models.api import Patent
from patent_fetcher.models.output_client import OutputClientResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LocalOutputClient(OutputClient):
    def output_patents(self, patents: list[Patent]) -> OutputClientResponse:
        """
        Writes out patents to local-disk as a gzip json with an arbitrary file name & location.

        Each gzip contains up to BUFFER number of items

        :param patents: List of Patent objects to write out
        """
        fname = f"./patents_{datetime.now().strftime("%y%m%d_%H%M%S")}.json.gz"
        logger.info(f"Attempting to flush {len(patents)} patents to {fname}")
        try:
            with gzip.open(fname, "wt", encoding="utf-8") as archive:
                archive.write(json.dumps([p.model_dump() for p in patents], default=str))
            logger.info(f"Successfully dumped {len(patents)} patents to {fname}")
        except Exception as e:
            # Does not halt execution on output failure - could be just this page/batch
            logger.error(f"Failed to dump {len(patents)} patents to {fname} - {e}")

        return OutputClientResponse(
            num_items_outputted=len(patents),
            output_info={
                "output_file": fname,
            }
        )