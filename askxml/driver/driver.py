from abc import ABC, abstractmethod
from typing import Generic

class Driver(ABC):
    def __init__(self, filename: str, table_definitions):
        pass

    @property
    @abstractmethod
    def table_hierarchy(self) -> dict:
        """
        Returns table structure. Example:
        "BASKET": {
            "APPLE": {},
            "BOX": {
                "ORANGE": {}
            }
        }
        """
        pass

    @abstractmethod
    def create_cursor(self):
        pass

    @abstractmethod
    def close(self):
        pass