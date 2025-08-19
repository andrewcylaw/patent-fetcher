from abc import ABC, abstractmethod

from patent_fetcher.models.api import Patent
from patent_fetcher.models.output_client import OutputClientResponse


class OutputClient(ABC):
    """
    Abstract base class for other output clients.
    """
    @abstractmethod
    def output_patents(self, patents: list[Patent]) -> OutputClientResponse:
        """
        Outputs the given list of patents according to the implementation.

        :param patents: List of Patent objects to write out
        :return: OutputClientResponse containing any relevant output information/metrics
        """
        pass
