from abc import ABC, abstractmethod
from typing import List

class Driver(ABC):
    def __init__(self, filename: str, table_definitions):
        pass

    @property
    @abstractmethod
    def table_names(self) -> List[str]:
        """
        Returns a list of defined table names
        """
        pass

    @abstractmethod
    def create_cursor(self):
        pass

    @abstractmethod
    def close(self):
        pass