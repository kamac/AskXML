from typing import List
from .xml2sql import convert
from .table import Table
import sqlite3
import tempfile
import os

class AskXML():
    def __init__(self, filename: str, table_definitions: List[Table] = None,
            persist_data: bool = True):
        """
        :param filename: Path to .xml file to open
        :param table_definitions: A list of table definitions
        :param persist_data: If enabled, changes to data will be saved to source XML file
        """
        self.persist_data = persist_data
        self.filename = filename

        sql_file = tempfile.TemporaryFile(mode='w+')
        convert(filename, sql_file, dict((table.table_name, table,) for table in table_definitions))
        sql_file.seek(0)

        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)

        self.__conn = sqlite3.connect(self.db_path)
        # fill database with data
        c = self.__conn.cursor()
        for query in sql_file:
            print(query)
            c.execute(query)
        self.__conn.commit()
        c.close()
        sql_file.close()

    def synchronize(self):
        """
        Saves changes to source XML file
        """
        pass

    def close(self):
        """
        Closes connection to XML document
        """
        self.synchronize()
        self.__conn.close()
        os.remove(self.db_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __getattr__(self, name):
        return getattr(self.__conn, name)