from abc import ABC, abstractmethod
from typing import List, Tuple

class Driver(ABC):
    def __init__(self, filename: str, table_definitions):
        pass

    @abstractmethod
    def get_xml_root(self):
        pass

    @abstractmethod
    def get_tables(self) -> Tuple[List[str], List[str]]:
        """
        Returns a tuple of (root table names, child table names)
        """
        pass

    @abstractmethod
    def create_cursor(self):
        pass

    @abstractmethod
    def close(self):
        pass