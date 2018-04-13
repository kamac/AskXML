from askxml.driver.sqlite_driver import SqliteDriver
from utils import TempFile
import unittest

_xml_file_simple =  """
<XML>
    <RootTable first="1" second="2">
        <Child></Child>
        <Child third="3"></Child>
    </RootTable>
    <RootTable />
    <RootTableSecond />
</XML>"""

_xml_file_no_children = "<XML></XML>"

class TestSqliteDriver(unittest.TestCase):
    def test_get_tables(self):
        with TempFile() as f:
            f.write(_xml_file_simple)
            with open(f.name, 'r') as fh:
                driver = SqliteDriver(source=fh, join_name='_parentId',
                    id_name='_id', table_definitions=None)

            root_tables, child_tables = driver.get_tables()
            self.assertTrue('RootTable'       in root_tables)
            self.assertTrue('RootTableSecond' in root_tables)
            self.assertEqual(len(root_tables), 2)
            self.assertTrue('RootTable_Child' in child_tables)
            self.assertEqual(len(child_tables), 1)
            driver.close()

        with TempFile() as f:
            f.write(_xml_file_no_children)
            with open(f.name, 'r') as fh:
                driver = SqliteDriver(source=fh, join_name='_parentId',
                    id_name='_id', table_definitions=None)
            root_tables, child_tables = driver.get_tables()
            self.assertEqual(len(root_tables), 0)
            self.assertEqual(len(child_tables), 0)
            driver.close()

if __name__ == '__main__':
    unittest.main()