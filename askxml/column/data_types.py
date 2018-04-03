"""
Supported column data types. Analogous to SQLite's.
Reference: https://www.sqlite.org/datatype3.html
"""

class DataType:
    """Defines the type of the stored value"""
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