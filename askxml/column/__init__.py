from .data_types import *
from .keys import *

class Column:
    """
    Column stores one XML attribute
    """

    def __init__(self, column_name: str, data_type: DataType, foreign_key: ForeignKey = None):
        """
        :param column_name: Name of SQL column
        :param data_type: Data type stored in column
        :param foreign_key: A foreign key constraint
        """
        self._column_name = column_name
        self._data_type = data_type
        if foreign_key:
            self._foreign_key = ForeignKey(foreign_key.foreign_table_name + '.' + foreign_key.foreign_column_name,
                column_name=column_name)
        else:
            self._foreign_key = None

    @property
    def column_name(self):
        return self._column_name

    @property
    def data_type(self):
        return self._data_type

    @property
    def foreign_key(self):
        return self._foreign_key

    def create_default(column_name: str):
        """Creates a default column definition for given column name."""
        return Column(column_name, Text())