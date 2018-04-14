from askxml import *
import xml.etree.ElementTree as ET
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

class TestSynchronize(unittest.TestCase):
    def test_preserves_structure(self):
        with tempfile.SpooledTemporaryFile(mode='w+') as f:
            f.write(_xml_file_simple)
            f.seek(0)
            AskXML(f).close()
            f.seek(0)
            tree = ET.parse(f)
            root = tree.getroot()

            self.assertEqual(root.tag, 'XML')
            self.assertFalse(root.attrib)
            # inspect root node
            children = [child for child in root]
            children_tags = [c.tag for c in children]
            self.assertTrue('RootTable' in children_tags)
            self.assertTrue('RootTableSecond' in children_tags)
            self.assertEqual(len(children), 3)

            RootTables = (c for c in children if c.tag == 'RootTable')
            # inspect first RootTable
            RootTable = next(RootTables)
            RootTable_children = [child for child in RootTable]
            RootTable_children_tags = [c.tag for c in RootTable_children]
            self.assertTrue('Child' in RootTable_children_tags)
            self.assertEqual(len(RootTable_children), 2)
            # inspect Children
            # make sure Child tags don't have any child nodes
            self.assertEqual(sum(1 for c in RootTable_children[0]), 0)
            self.assertEqual(sum(1 for c in RootTable_children[1]), 0)
            self.assertFalse(RootTable_children[0].attrib)
            self.assertEqual(RootTable_children[0].text, 'Hello')
            self.assertEqual(RootTable_children[1].attrib, {'third': '3'})
            self.assertFalse(RootTable_children[1].text)

            # inspect second RootTable
            RootTable = next(RootTables)
            self.assertEqual(sum(1 for c in RootTable), 0)
            self.assertFalse(RootTable.attrib)

            # inspect RootTableSecond
            RootTableSecond = next(c for c in children if c.tag == 'RootTableSecond')
            self.assertEqual(sum(1 for c in RootTableSecond), 0)
            self.assertFalse(RootTableSecond.attrib)
            self.assertEqual(RootTableSecond.text, 'Hi')

if __name__ == '__main__':
    unittest.main()