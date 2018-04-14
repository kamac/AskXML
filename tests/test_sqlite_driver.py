from askxml.driver.sqlite_driver import SqliteDriver
from askxml.table import Table
from askxml.column import *
import tempfile
import unittest

_xml_file_simple =  """
<XML>
    <RootTable first="1" second="2">
        <Child>Hello</Child>
        <Child third="3"></Child>
    </RootTable>
    <RootTable />
    <RootTableSecond>Hi</RootTableSecond>
</XML>"""

_xml_file_no_children = "<XML></XML>"

class TestSqliteDriver(unittest.TestCase):
    def test_get_tables(self):
        # test simple xml file
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_simple)
            f.seek(0)
            driver = SqliteDriver(source=f)

            root_tables, child_tables = driver.get_tables()
            self.assertTrue('RootTable'       in root_tables)
            self.assertTrue('RootTableSecond' in root_tables)
            self.assertEqual(len(root_tables), 2)
            self.assertTrue('RootTable_Child' in child_tables)
            self.assertEqual(len(child_tables), 1)
            driver.close()

        # test xml file without any tables
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_no_children)
            f.seek(0)
            driver = SqliteDriver(source=f)
            root_tables, child_tables = driver.get_tables()
            self.assertEqual(len(root_tables), 0)
            self.assertEqual(len(child_tables), 0)
            driver.close()

        # test xml file with no nodes, but defined tables
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_no_children)
            f.seek(0)
            driver = SqliteDriver(source=f, table_definitions=[Table('sometable')])
            root_tables, child_tables = driver.get_tables()
            self.assertTrue('sometable' in root_tables)
            self.assertEqual(len(root_tables), 1)
            self.assertEqual(len(child_tables), 0)
            driver.close()

    def test_get_attributes(self):
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_simple)
            f.seek(0)
            driver = SqliteDriver(source=f)
            cursor = driver.create_cursor()
            result = cursor.execute("SELECT first, second FROM RootTable WHERE _id=1").fetchall()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], '1')
            self.assertEqual(result[0][1], '2')
            result = cursor.execute("SELECT third FROM RootTable_Child").fetchall()
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0][0], None)
            self.assertEqual(result[1][0], '3')
            cursor.close()
            driver.close()

    def test_attribute_types(self):
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_simple)
            f.seek(0)
            driver = SqliteDriver(source=f, table_definitions=[Table('RootTable', Column('first', Integer()))])
            cursor = driver.create_cursor()
            result = cursor.execute("SELECT first, second FROM RootTable WHERE _id=1").fetchall()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], 1)
            self.assertEqual(result[0][1], '2')
            cursor.close()
            driver.close()

    def test_node_text(self):
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_simple)
            f.seek(0)
            driver = SqliteDriver(source=f)
            cursor = driver.create_cursor()
            result = cursor.execute("SELECT _text FROM RootTable_Child ORDER BY _id ASC").fetchall()
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0][0], 'Hello')
            self.assertEqual(result[1][0], None)
            cursor.close()
            driver.close()

if __name__ == '__main__':
    unittest.main()