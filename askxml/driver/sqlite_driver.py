from typing import Dict, AbstractSet, List, Tuple
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

class EmptyTableException(Exception):
    pass

class SqliteDriver(Driver):
    """
    Sqlite Driver works by setting up a .sqlite copy of XML document,
    and then running statements on it.
    """

    def __init__(self, source, table_definitions = None, join_name: str = '_parentId', id_name: str = '_id',
        text_name: str = '_text', in_memory_db: bool = False):
        """
        :param source: Path to .xml file to open, or file handle
        :param table_definitions: A dict of table name as keys table definitions as values
        :param join_name: Name of the column that stores parent's ID
        :param id_name: Name of the column that stores node's ID
        :param text_name: Name of the column that stores node's text
        :param in_memory_db: If set to True, sqlite's database will be stored in RAM rather than as
            a temporary file on disk.
        """
        self.join_name = join_name
        self.id_name = id_name
        sql_file = tempfile.TemporaryFile(mode='w+')
        if table_definitions:
            # convert table definitions from a list of tables into a dict
            # where key is table name and value is a Table object
            table_definitions = dict((table.table_name, table,) for table in table_definitions)

        self.__converter = Converter(source, sql_file,
            table_definitions=table_definitions, text_name=text_name,
            join_name=join_name, id_name=id_name)
        sql_file.seek(0)

        if not in_memory_db:
            handle, self.db_path = tempfile.mkstemp(suffix='.db')
            os.close(handle)
        else:
            self.db_path = ':memory:'

        self._conn = sqlite3.connect(self.db_path)
        # fill database with data
        cursor = self._conn.cursor()
        for query in sql_file:
            cursor.execute(query)
        cursor.close()
        self._conn.commit()
        sql_file.close()

    def get_xml_root(self):
        return self.__converter.root_name, self.__converter.root_attrib

    def get_tables(self) -> Tuple[List[str], List[str]]:
        cursor = self.create_cursor()
        try:
            root_tables = []
            child_tables = []
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for table_name in tables.fetchall():
                columns = cursor.execute("PRAGMA table_info('{}')".format(table_name[0])).fetchall()
                columns = [c[1] for c in columns]
                if self.join_name not in columns:
                    root_tables.append(table_name[0])
                else:
                    child_tables.append(table_name[0])
            return root_tables, child_tables
        finally:
            cursor.close()

    def create_cursor(self):
        return self._conn.cursor()

    def close(self):
        self._conn.close()
        if self.db_path != ':memory:':
            os.remove(self.db_path)

class Converter:
    def __init__(self, source, outfile, table_definitions: Dict[str, table.Table] = None,
        text_name: str = None, join_name: str = None, id_name: str = None):
        """
        Converts an XML file to a .sqlite script

        :param source: Path to .xml file to open, or file handle
        :param outfile: File handle to where resulting .sql will be stored
        :param table_definitions: A dict of table name as keys table definitions as values
        :param join_name: Name of the column that stores parent's ID. Set to None to not join.
        :param id_name: Name of the column that stores node's ID. Set to None to not generate an ID.
        """
        if not table_definitions:
            table_definitions = {}

        self.table_definitions = table_definitions
        self.join_name = join_name
        self.id_name = id_name
        self.text_name = text_name
        # a pair of table_name : last free id
        self.id_cache: Dict[str, int] = {}
        # a set of table names which tells us in a quick way
        # whether we've already altered a table with id, join id and text column
        self._generated_meta_columns_cache: AbstractSet[str] = set()

        self.xmliter = xml.iterparse(source, events=("start", "end"))
        _, root = next(self.xmliter)
        self.root_name = root.tag
        self.root_attrib = root.attrib
        # a dict that holds all found tables and their columns
        self.tables: Dict[str, AbstractSet[str]] = {}
        # update found tables with user defined table definitions
        for table_name, table_definition in table_definitions.items():
            # also generate join keys for predefined table
            self.__generate_table_meta_columns(table_name)
            self.tables[table_name] = set(column_definition.column_name for column_definition in table_definition.column_definitions)

        # generate insert queries in a temporary file
        self.inserts_file = tempfile.TemporaryFile(mode='w+')
        self.__parse_node(root, None)
        self.inserts_file.seek(0)

        # generate create table statements
        constraint_definitions = []
        for table_name, columns in self.tables.items():
            table_definition = table_definitions.get(table_name, None)

            # create column parameters (column_name column_type [key])
            column_definitions = []
            for column_name in columns:
                column_info = None
                try:
                    column_info = table_definition.get_column(column_name)
                except KeyError:
                    column_info = column.Column.create_default(column_name)

                column_definition = column_name + ' ' + str(column_info.data_type)
                if column_info.foreign_key:
                    column_definition = column_definition + ' REFERENCES {}({}) DEFERRABLE INITIALLY DEFERRED'.format(
                        column_info.foreign_key.foreign_table_name,
                        column_info.foreign_key.foreign_column_name
                    )
                column_definitions.append(column_definition)

            if not column_definitions:
                raise EmptyTableException("SQLite cannot create an empty table '{}'".format(table_name))

            # create constraints
            if table_definition:
                for constraint in table_definition.constraint_definitions:
                    if isinstance(constraint, column.UniqueIndex) or isinstance(constraint, column.Index):
                        constraint_name = '_'.join(constraint.column_names) + '_index'
                        unique_sql = 'UNIQUE' if isinstance(constraint, column.UniqueIndex) else ''
                        constraint_definitions.append('CREATE {} INDEX {} ON {} ({})'.format(
                            unique_sql,
                            constraint_name,
                            table_name,
                            ','.join(constraint.column_names)))
                    elif isinstance(constraint, column.ForeignKey):
                        for i, definition in enumerate(column_definitions):
                            if definition.startswith(constraint.column_name + ' '):
                                column_definitions[i] = definition + ' REFERENCES {}({}) DEFERRABLE INITIALLY DEFERRED'.format(
                                    constraint.foreign_table_name,
                                    constraint.foreign_column_name
                                )
                    elif isinstance(constraint, column.PrimaryKey):
                        for i, definition in enumerate(column_definitions):
                            if definition.startswith(constraint.column_name + ' '):
                                column_definitions[i] = definition + ' PRIMARY KEY'
                                break

            outfile.write('CREATE TABLE {} ({});\n'.format(table_name, ','.join(column_definitions)))

        # copy insert queries from temp file to out file
        for line in self.inserts_file:
            outfile.write(line)

        # generate constraints
        for constraint in constraint_definitions:
            outfile.write(constraint + '\n')

        self.inserts_file.close()

    def __generate_table_meta_columns(self, table_name):
        self._generated_meta_columns_cache.add(table_name)
        table_definition = self.table_definitions[table_name]
        if self.id_name:
            # generate an id column
            table_definition.column_definitions.append(column.Column(self.id_name, column.Integer()))
            table_definition.constraint_definitions.append(column.PrimaryKey(self.id_name))
        # generate a join ID column
        if self.join_name and table_name.rfind('_') > -1:
            table_definition.column_definitions.append(column.Column(self.join_name, column.Integer(),
                column.ForeignKey(table_name[:table_name.rfind('_')] + '.' + self.id_name)))
        # generate a text column
        if self.text_name:
            table_definition.column_definitions.append(column.Column(self.text_name, column.Text()))

    def __parse_node(self, node, prev_node_attrib, table_scope=''):
        attributes = node.attrib
        if prev_node_attrib is not None:
            table_name = table_scope + node.tag
            table_definition = self.table_definitions.get(table_name, None)
            # if table was not defined, define it
            if not table_definition:
                table_definition = table.Table(table_name)
                self.table_definitions[table_name] = table_definition

            # update attributes with joined ID and ID
            if self.id_name:
                if table_name not in self.id_cache:
                    self.id_cache[table_name] = 1
                attributes.update({ self.id_name: str(self.id_cache[table_name]) })
                self.id_cache[table_name] = self.id_cache[table_name] + 1

                if self.id_name in prev_node_attrib and self.join_name:
                    attributes.update({self.join_name: prev_node_attrib[self.id_name]})

            stripped_text = node.text.strip() if node.text else None
            if self.text_name and stripped_text:
                attributes.update({ self.text_name: stripped_text })

            # update table definition with meta columns if needed
            if self.id_name or self.join_name or self.text_name:
                if table_name not in self._generated_meta_columns_cache:
                    self.__generate_table_meta_columns(table_name)

            column_values = []
            for column_name, value in attributes.items():
                try:
                    data_type = table_definition.get_column(column_name).data_type
                except KeyError as e:
                    data_type = column.Column.create_default(column_name).data_type

                if isinstance(data_type, column.Text) or isinstance(data_type, column.Blob):
                    column_values.append("'" + value.replace("'", "''").replace('\n', '\\n') + "'")
                else:
                    column_values.append(value)

            self.inserts_file.write('INSERT INTO {} ({}) VALUES ({});\n'.format(
                table_name,
                ','.join(attributes.keys()),
                ','.join(column_values)
            ))

            # update table definitions
            if not table_name in self.tables:
                self.tables[table_name] = set(node.attrib.keys())
            else:
                self.tables[table_name].update(node.attrib.keys())

            table_scope = table_name + '_'

        # parse child nodes
        while True:
            event, child_node = next(self.xmliter)
            if event == 'end' and child_node.tag == node.tag:
                break
            else:
                self.__parse_node(child_node, attributes, table_scope=table_scope)

        # prevent eating up too much memory
        node.clear()
