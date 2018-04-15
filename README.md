# AskXML
Run SQL statements on XML documents

```xml
<xml>
    <fruit color='green'>tasty kiwi</fruit>
    <fruit color='dark green'>old kiwi</fruit>
    <fruit color='green'>apple</fruit>
</xml>
```

```python

>>> from askxml import AskXML

>>> conn = AskXML('file.xml')
# get an SQL cursor object
>>> c = conn.cursor()
>>> results = c.execute("SELECT color FROM fruit WHERE _text LIKE '% kiwi'")
>>> for row in results.fetchall():
>>>    print(row)
[('green'), ('dark green')]

# cleanup
>>> c.close()
>>> conn.close()
```

## BUT WHY?

There are data dumps like stack exchange's, stored in XML. They're big, so fitting them whole into memory is not desired. With AskXML you can query things fast, and rather comfortably (provided you know SQL).

Before you go any further though, it's very possible your task can be achieved with XPATH and ElementTree XML API, so give that a look if you haven't heard of it.

## Installation

AskXML requires Python 3.5+. Best way to install is to get it with pip:

`pip install askxml`

## Usage

#### Adding indexes and defining columns

If you want to add indexes, columns or set attribute types, you can pass a list of table definitions:

```python

from askxml import *
tables = [
    Table('fruit',
        Column('age', Integer()),
        Index('age'))
]
with AskXML('file.xml', table_definitions=tables) as conn:
    c = conn.cursor()
    c.execute("UPDATE fruit SET age = 5 WHERE _text = 'tasty kiwi'")
    c.close()
```

You don't need to define all existing columns or tables. If a definition was not found, it's created with all column types being Text by default.

#### Node hierarchy

If you want to find nodes that are children of another node by attribute:

```xml

<xml>
    <someParent name='Jerry'>
        <someChild name='Morty' />
        <someChild name='Summer' />
    </someParent>
</xml>
```

```python

from askxml import *
with AskXML('file.xml') as conn:
    c = conn.cursor()
    results = c.execute("""
        SELECT name FROM someParent_someChild as child
        INNER JOIN someParent as parent ON parent._id = child._parentId
        WHERE parent.name = 'Jerry'
    """)
    for row in results.fetchall():
        print(row)
    c.close()
```

This will print `[('Morty'), ('Summer')]`.

#### Inserting new data

If you want to add a new tag:

```python
cursor.execute("INSERT INTO fruit (color, _text) VALUES ('red', 'strawberry')")
```

Or if your nodes have a hierarchy:

```python
cursor.execute("INSERT INTO someParent_someChild (name, _parentId) VALUES ('a baby', 1)")
```

## Contributing

Any contributions are welcome.

## License

AskXML is licensed under [MIT license](https://github.com/kamac/AskXML/blob/master/LICENSE)