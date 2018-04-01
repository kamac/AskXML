from typing import Dict
from .xml2sql import convert
from .column import ColumnInfo
import sqlite3
import tempfile
import os

class AskXML():
    def __init__(self, filename: str, column_annotations: Dict[str, Dict[str, ColumnInfo]] = None):
        """
        :param filename: Path to .xml file to open
        :param column_annotations: A dictionary specifying column properties. First key is table name,
            second is column name.
        """
        sql_file = tempfile.TemporaryFile(mode='w+')
        convert(filename, sql_file, column_annotations)
        sql_file.seek(0)

        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)

        self.__conn = sqlite3.connect(self.db_path)
        # fill database with data
        c = self.__conn.cursor()
        for query in sql_file:
            c.execute(query)
        self.__conn.commit()
        c.close()
        sql_file.close()

    def save(self):
        """
        Saves changes to source XML file
        """
        pass

    def close(self):
        self.__conn.close()
        os.remove(self.db_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __getattr__(self, name):
        return getattr(self.__conn, name)