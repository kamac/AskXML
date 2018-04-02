from askxml import (AskXML, Integer, UniqueIndex, PrimaryKey, Table, Column)

if __name__ == '__main__':
    table_definitions = [
        Table('TAGS',
            Column('Id', Integer()),
            PrimaryKey('Id')
        ),
        Table('TAGS_TAG',
            Column('Id', Integer()),
            PrimaryKey('Id'),
            UniqueIndex('name')
        )
    ]
    conn = AskXML('test.xml', table_definitions=table_definitions)

    c = conn.cursor()
    c.execute("SELECT * FROM TAGS_TAG WHERE name LIKE 'kiwi%'")
    result_set = c.fetchall()
    for row in result_set:
        print(row)
    c.close()
    conn.close()