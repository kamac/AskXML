from askxml import (AskXML, Integer, UniqueIndex, PrimaryKey, Table, Column,
    ForeignKey)

if __name__ == '__main__':
    table_definitions = [
        Table('TAGS_TAG',
            Column('Id', Integer()),
            UniqueIndex('name')
        )
    ]
    conn = AskXML('test.xml', table_definitions=table_definitions)

    c = conn.cursor()

    c.execute("SELECT * FROM TAGS_TAG WHERE name LIKE 'kiwi%'")
    for row in c.fetchall():
        print(row)

    c.execute("""SELECT tag.name FROM TAGS_TAG AS tag
        INNER JOIN TAGS AS parent ON parent._id = tag._parentId
        WHERE parent.name = 'SELECT ME'""")
    for row in c.fetchall():
        print(row)

    c.close()
    conn.close()