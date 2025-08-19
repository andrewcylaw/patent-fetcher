from enum import Enum

from patent_fetcher.clients.output.local import LocalOutputClient
from patent_fetcher.clients.output.sqlite import SQLiteOutputClient


class Output(Enum):
    """
    Enum indicating output location:
    - local: dump to disk as a json gzip
    - sqlite: write out to sqlite as defined in the environment settings
    """
    LOCAL = "local"
    SQLITE = "sqlite"

# Consciously doing a simple mapping of a user input to a concrete class
# a better option might be something like a registry pattern
OUTPUT_CLIENT = {
    Output.LOCAL: LocalOutputClient,
    Output.SQLITE: SQLiteOutputClient,
}