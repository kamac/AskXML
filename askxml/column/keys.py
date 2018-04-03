"""
Supported column keys
"""

class Key:
    """Defines whether column is indexed and how"""
    def __init__(self, column_name: str, *args):
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
    def __init__(self, column_name: str):
        """
        :param column_name: Column affected by this key
        """
        super().__init__(column_name)

class ForeignKey(Key):
    def __init__(self, foreign_column: str, column_name: str = None):
        """
        :param foreign_column: Full foreign column name. Example: SOME_PARENT.id
        :param column_name: Column affected by this key.
        """
        super().__init__(column_name)
        self._foreign_column_name, self._foreign_table_name = foreign_column.split('.')

    @property
    def foreign_column_name(self):
        return self._foreign_column_name

    @property
    def foreign_table_name(self):
        return self._foreign_table_name