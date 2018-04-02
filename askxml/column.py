"""
This file defines supported data types and keys.
Data types are analogous to SQLite data types. Reference: https://www.sqlite.org/datatype3.html
"""

# data types
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

# keys
class Key:
    """Defines whether column is indexed and how"""
    def __init__(self, column_name, *args):
        """
        :param column_name: Column affected by this key
        :param *args: A list of additional column names affected by key. Specify this
            to create a composite key
        """
        self._column_name = column_name
        self._column_names = frozenset([column_name] + list(args))

    @property
    def column_names(self):
        return self._column_names

    @property
    def column_name(self):
        return self._column_name

class UniqueIndex(Key):
    pass

class Index(Key):
    pass

class PrimaryKey(Key):
    def __init__(self, column_name):
        """
        :param column_name: Column affected by this key
        """
        super().__init__(column_name)

class Column:
    def __init__(self, column_name: str, data_type: DataType):
        self._column_name = column_name
        self._data_type = data_type

    @property
    def column_name(self):
        return self._column_name

    @property
    def data_type(self):
        return self._data_type

    def create_default(column_name: str):
        """Creates a default column definition for given column name."""
        return Column(column_name, Text())