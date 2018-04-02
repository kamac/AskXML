from typing import Dict, AbstractSet, List
from abc import abstractmethod
from askxml import column, table
from .driver import Driver
try:
    import lxml.etree as xml
except ModuleNotFoundError:
    import xml.etree.cElementTree as xml
import tempfile
import os
import sqlite3

class SqliteDriver(Driver):
    """
    Sqlite Driver works by setting up a .sqlite copy of XML document,
    and then running statements on it.
    """
    def __init__(self, filename: str, table_definitions):
        sql_file = tempfile.TemporaryFile(mode='w+')
        convert(filename, sql_file, dict((table.table_name, table,) for table in table_definitions))
        sql_file.seek(0)

        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)

        self._conn = sqlite3.connect(self.db_path)
        # fill database with data
        self._cursor = self._conn.cursor()
        for query in sql_file:
            self._cursor.execute(query)
        self._conn.commit()
        sql_file.close()

    @property
    def table_names(self) -> List[str]:
        self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        result_set = self._cursor.fetchall()
        return [r[0] for r in result_set]

    def create_cursor(self):
        return self._conn.cursor()

    def close(self):
        self._cursor.close()
        self._conn.close()
        os.remove(self.db_path)

def convert(filename: str, outfile, table_definitions: Dict[str, table.Table] = None):
    """
    Converts an XML file to a .sqlite script

    :param filename: Path to .xml file to open
    :param outfile: File handle where resulting .sql will be stored
    :param table_definitions: A dict of table name as keys table definitions as values
    """
    xmliter = xml.iterparse(filename, events=("start", "end"))
    _, root = next(xmliter)
    # a dict that holds all found tables and their columns
    tables: Dict[str, AbstractSet[str]] = {}

    # generate insert queries in a temporary file
    inserts_file = tempfile.TemporaryFile(mode='w+')
    __parseNode(root, xmliter, tables, inserts_file, table_definitions=table_definitions)
    inserts_file.seek(0)

    # generate create table queries
    constraint_definitions = []
    for table_name, columns in tables.items():
        # create column parameters (column_name column_type [key])
        column_definitions = []
        for column_name in columns:
            column_info = None
            try:
                column_info = table_definitions[table_name].get_column(column_name)
            except (KeyError, AttributeError):
                column_info = column.Column.create_default(column_name)

            column_definitions.append(column_name + ' ' + str(column_info.data_type))

        # create constraints
        if table_name in table_definitions:
            for constraint in table_definitions[table_name].constraint_definitions:
                if isinstance(constraint, column.UniqueIndex) or isinstance(constraint, column.Index):
                    constraint_name = '_'.join(constraint.column_names) + '_index'
                    unique_sql = 'UNIQUE' if isinstance(constraint, column.UniqueIndex) else ''
                    constraint_definitions.append('CREATE {} INDEX {} ON {} ({})'.format(
                        unique_sql,
                        constraint_name,
                        table_name,
                        ','.join(constraint.column_names)))
                elif isinstance(constraint, column.PrimaryKey):
                    for i, definition in enumerate(column_definitions):
                        if definition.startswith(constraint.column_name + ' '):
                            column_definitions[i] = definition + ' PRIMARY KEY'
                            break

        outfile.write('CREATE TABLE {} ({});\n'.format(table_name, ','.join(column_definitions)))

    # copy insert queries from temp file to out file
    for line in inserts_file:
        outfile.write(line)

    # generate constraints
    for constraint in constraint_definitions:
        outfile.write(constraint + '\n')

    inserts_file.close()

def __parseNode(node, xmliter, tables, file, table_definitions=None, table_scope=None):
    if table_scope is not None:
        table_name = table_scope + node.tag.upper()
        table_scope = table_name + '_'

        column_values = []
        for column_name, value in node.attrib.items():
            try:
                data_type = table_definitions[table_name].get_column(column_name).data_type
            except (KeyError, AttributeError) as e:
                data_type = column.Column.create_default(column_name).data_type

            if isinstance(data_type, column.Text) or isinstance(data_type, column.Blob):
                column_values.append("'" + value.replace("'", "''") + "'")
            else:
                column_values.append(value)

        file.write('INSERT INTO {} ({}) VALUES ({});\n'.format(
            table_name,
            ','.join(node.attrib.keys()),
            ','.join(column_values)
        ))

        # update table definitions
        if not table_name in tables:
            tables[table_name] = set(node.attrib.keys())
        else:
            tables[table_name].update(node.attrib.keys())
    else:
        table_scope = ''

    # parse child nodes
    while True:
        event, child_node = next(xmliter)
        if event == 'end' and child_node.tag == node.tag:
            break
        else:
            __parseNode(child_node, xmliter, tables, file, table_definitions=table_definitions, table_scope=table_scope)

    # prevent eating up too much memory
    node.clear()
