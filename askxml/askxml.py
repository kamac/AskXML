from importlib import import_module
from typing import List
from .table import Table
import tempfile
import os

class AskXML:
    def __init__(self, filename: str, table_definitions: List[Table] = None,
            persist_data: bool = True, driver = 'sqlite'):
        """
        :param filename: Path to .xml file to open
        :param table_definitions: A list of table definitions
        :param persist_data: If enabled, changes to data will be saved to source XML file
        :param driver: Driver used to implement sql functionality. Can be a string or an object implementing Driver
        """
        self.persist_data = persist_data
        self.filename = filename
        if not hasattr(driver, '__call__'):
            driver = getattr(import_module('askxml.driver.' + driver + '_driver'), driver.capitalize() + 'Driver')

        self._driver = driver(filename, table_definitions)

    def synchronize(self):
        """
        Saves changes to source XML file
        """
        if not self.persist_data:
            return

        #cursor = self._driver.create_cursor()
        #print(self._driver.table_names)
        raise NotImplementedError()

    def close(self):
        """
        Closes connection to XML document
        """
        self.synchronize()
        self._driver.close()

    def cursor(self):
        return self._driver.create_cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()