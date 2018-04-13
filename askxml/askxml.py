from importlib import import_module
from typing import List
from .table import Table
import tempfile
import os

class AskXML:
    def __init__(self, source, table_definitions: List[Table] = None,
            persist_data: bool = True, driver = 'sqlite', join_name='_parentId', id_name='_id',
            serialize_ident: str = '  ', *args, **kwargs):
        """
        :param source: Path to .xml file to open, or file handle
        :param table_definitions: A list of table definitions
        :param persist_data: If enabled, changes to data will be saved to source XML file
        :param driver: Driver used to implement sql functionality. Can be a string or an object implementing Driver
        :param join_name: Name of the column that stores parent's ID
        :param id_name: Name of the column that stores node's ID
        :param serialize_ident: Identation to use when serializing data to XML
        """
        self.persist_data = persist_data
        self.filename = filename
        self.join_name = join_name
        self.id_name = id_name
        self.serialize_ident = serialize_ident
        if not hasattr(driver, '__call__'):
            driver = getattr(import_module('askxml.driver.' + driver + '_driver'), driver.capitalize() + 'Driver')

        self._driver = driver(filename, table_definitions, join_name=join_name, id_name=id_name, *args, **kwargs)

    def synchronize(self):
        """
        Saves changes to source XML file
        """
        if not self.persist_data:
            return

        self._sync_cursor = self._driver.create_cursor()
        try:
            self._sync_file = open(self.filename, 'w')
            root_name, root_attrib = self._driver.get_xml_root()
            self._sync_file.write("<{tag}{properties}>\n".format(
                tag=root_name,
                properties=self._serialize_properties(root_attrib.items())))

            root_tables, self.__child_tables = self._driver.get_tables()
            for root_tag in root_tables:
                root_tags_data = self._sync_cursor.execute("SELECT * FROM {from_table}".format(from_table=root_tag))
                self._synchronize_tags(root_tags_data.fetchall(), table_scope=root_tag, ident=self.serialize_ident)
            self._sync_file.write("</{tag}>\n".format(tag=root_name))
        finally:
            self._sync_file.close()
            self._sync_cursor.close()

    def _serialize_properties(self, properties):
        """
        Serialize a list of properties to a XML representation

        :param properties: A list of tuples (property_name, property_value,)
        """
        # filter out properties whose value is None, or name is join_name or id_name
        filtered_properties = [p for p in properties if p[1] is not None and p[0] != self.join_name\
            and p[0] != self.id_name]
        if len(filtered_properties) > 0:
            return ' ' + ' '.join('{}="{}"'.format(name, val.replace('"', '&quot;')) for name, val in filtered_properties)
        else:
            return ''

    def _synchronize_tags(self, tags_data, table_scope='', ident=''):
        field_names = [desc[0] for desc in self._sync_cursor.description]
        for tag_data in tags_data:
            name_value_properties = zip(field_names, tag_data)
            tag_id = tag_data[field_names.index(self.id_name)]
            tag_name = table_scope.split('_')[-1]
            child_tables = [c for c in self.__child_tables if c[:c.rfind('_')] == table_scope]

            self._sync_file.write('{ident}<{tag_name}{properties}{immediate_close}>\n'.format(
                ident=ident,
                tag_name=tag_name,
                properties=self._serialize_properties(name_value_properties),
                immediate_close=' /' if not child_tables else ''))

            # synchronize this tag's children
            for child_tag in child_tables:
                chidren_data = self._sync_cursor.execute("""SELECT a.* FROM {from_table} AS a
                    INNER JOIN {parent_table} AS b ON a.{join_name} = b.{id_name}
                    WHERE b.{id_name} = {parent_id}""".format(
                        from_table=child_tag,
                        parent_table=table_scope,
                        join_name=self.join_name,
                        id_name=self.id_name,
                        parent_id=tag_id
                    ))
                self._synchronize_tags(chidren_data.fetchall(), table_scope=child_tag, ident=ident + self.serialize_ident)

            if child_tables:
                # close parent tag
                self._sync_file.write('{ident}</{tag_name}>\n'.format(ident=ident, tag_name=tag_name))

    def close(self):
        """
        Closes connection to XML document
        """
        self.synchronize()
        self._driver.close()

    def cursor(self):
        return self._driver.create_cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()