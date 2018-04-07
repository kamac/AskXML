from askxml import (AskXML, Integer, UniqueIndex, PrimaryKey, Table, Column,
    ForeignKey)

if __name__ == '__main__':
    table_definitions = [
        Table('tags_tag',
            Column('Id', Integer()),
            UniqueIndex('name')
        )
    ]
    conn = AskXML('test.xml', table_definitions=table_definitions, in_memory_db=True)

    c = conn.cursor()

    print("select all tags whose name begin with kiwi")
    c.execute("SELECT _id, name FROM tags_tag WHERE name LIKE 'kiwi%'")
    for row in c.fetchall():
        print(row)

    print("select all tags under tag with specified name")
    c.execute("""SELECT tag.name FROM tags_tag AS tag
        INNER JOIN tags AS parent ON parent._id = tag._parentId
        WHERE parent.name = 'SELECT ME'""")
    for row in c.fetchall():
        print(row)

    print("insert a new tag into otherContainer")
    c.execute("INSERT INTO otherContainer_tag (_parentId, name) VALUES (1, 'oink')")

    c.close()
    conn.close()