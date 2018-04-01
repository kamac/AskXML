from typing import Dict, AbstractSet
from . import column
import xml.etree.cElementTree as xml
import tempfile

def convert(filename: str, outfile, column_annotations: Dict[str, Dict[str, column.ColumnInfo]] = None):
    """
    Converts an XML file to a SQL script

    :param filename: Path to .xml file to open
    :param outfile: File handle where resulting .sql will be stored
    :param column_annotations: A dictionary specifying column properties
    """
    xmliter = xml.iterparse(filename, events=("start", "end"))
    _, root = next(xmliter)
    tables: Dict[str, AbstractSet[str]] = {}

    # generate insert queries in a temporary file
    inserts_file = tempfile.TemporaryFile(mode='w+')
    __parseNode(root, xmliter, tables, inserts_file, column_annotations=column_annotations)
    inserts_file.seek(0)

    # generate create table queries
    for table_name, columns in tables.items():
        column_definitions = []
        for column_name in columns:
            column_info = None
            try:
                column_info = column_annotations[table_name][column_name]
            except (KeyError, TypeError):
                column_info = column.ColumnInfo(data_type=column.Text())

            column_definition = column_name
            column_definition = column_definition + ' ' + str(column_info.data_type)
            if column_info and column_info.is_primary_key:
                column_definition = column_definition + ' PRIMARY KEY'
            column_definitions.append(column_definition)

        outfile.write('CREATE TABLE {} ({});\n'.format(table_name, ','.join(column_definitions)))

    # copy insert queries from temp file to out file
    for line in inserts_file:
        outfile.write(line)

    inserts_file.close()

def __parseNode(node, xmliter, tables, file, column_annotations=None, table_scope=None):
    if table_scope is not None:
        table_name = table_scope + node.tag.upper()
        table_scope = table_name + '_'

        column_values = []
        for column_name, value in node.attrib.items():
            try:
                data_type = column_annotations[table_name][column_name].data_type
            except (KeyError, TypeError):
                data_type = column.Text()

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

    while True:
        event, child_node = next(xmliter)
        if event == 'end' and child_node.tag == node.tag:
            break
        else:
            __parseNode(child_node, xmliter, tables, file, column_annotations=column_annotations, table_scope=table_scope)
