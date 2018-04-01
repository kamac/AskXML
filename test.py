from askxml import AskXML, ColumnInfo, Integer

if __name__ == '__main__':
    conn = AskXML('test.xml', column_annotations={
        'TAGS':     { 'Id': ColumnInfo(Integer(), is_primary_key=True) },
        'TAGS_TAG': { 'Id': ColumnInfo(Integer(), is_primary_key=True) }
    })
    c = conn.cursor()
    c.execute("SELECT * FROM TAGS_TAG WHERE name LIKE 'kiwi%'")
    result_set = c.fetchall()
    for row in result_set:
        print(row)
    c.close()
    conn.close()