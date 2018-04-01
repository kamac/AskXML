"""
This file defines supported data types.
They're analogous to SQLite data types. Reference: https://www.sqlite.org/datatype3.html
"""
from typing import NamedTuple

class DataType:
    def __str__(self):
        raise NotImplementedError()

class Integer(DataType):
    def __str__(self):
        return "INTEGER"

class Real(DataType):
    def __str__(self):
        return "REAL"

class Text(DataType):
    def __str__(self):
        return "TEXT"

class Blob(DataType):
    def __str__(self):
        return "BLOB"

class ColumnInfo(NamedTuple):
    data_type: DataType
    is_primary_key: bool = None