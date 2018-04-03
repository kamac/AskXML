from importlib import import_module
from typing import List
from .table import Table
import tempfile
import os

class AskXML:
    def __init__(self, filename: str, table_definitions: List[Table] = None,
            persist_data: bool = True, driver = 'sqlite', *args, **kwargs):
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

        self._driver = driver(filename, table_definitions, *args, **kwargs)

    def synchronize(self):
        """
        Saves changes to source XML file
        """
        if not self.persist_data:
            return

        cursor = self._driver.create_cursor()
        try:
            '''with open(self.filename + '_saved', 'w') as f:
                for key, table_name in self._driver.table_hierarchy.items():
                    result_set = cursor.execute("""SELECT * FROM {from_table} AS a
                        INNER JOIN {parent_table} AS b ON a.{join_name} = b.{id_name}
                        WHERE b.{id_name} = {parent_id}""".format(
                            from_table = ))'''
            pass
        finally:
            cursor.close()

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