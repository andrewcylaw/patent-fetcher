import logging
import sqlite3

from patent_fetcher.clients.output.base_client import OutputClient
from patent_fetcher.models.api import Patent
from patent_fetcher.models.output_client import OutputClientResponse
from patent_fetcher.settings import cli_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SQLiteOutputClient(OutputClient):
    def output_patents(self, patents: list[Patent]) -> OutputClientResponse:
        """
        Attempts to write out the given list of patents to a SQLite instance.

        Implementation note:
            I'm deliberately using plain SQL text - a better approach depending on performance/correctness might wrap it
            in an ORM like SQLAlchemy or offload it to a different service.

        :param patents: List of Patent objects to write out
        :return: An OutputClientResponse containing information about the output procedure
        """
        logger.info(f"Attempting to flush {len(patents)} patents to SQLite {cli_settings.sqlite_db}")
        output = OutputClientResponse()
        try:
            # <!> this is done on purpose for demonstration purposes <!>
            # A production approach would have:
            #  - ORM / actual table types
            #  - schema migration (eg Flyway/liquibase/Django ORM)
            with sqlite3.connect(cli_settings.sqlite_db) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS patent (data TEXT)")
                conn.executemany("INSERT INTO patent (data) VALUES (?)", [(p.model_dump_json(),) for p in patents])
                output.num_items_outputted = int(conn.execute("SELECT COUNT(*) FROM patent;").fetchone()[0])
        except Exception as e:
            raise ValueError(f"Failed to write {len(patents)} patents out to sqlite - {e}")

        return output
