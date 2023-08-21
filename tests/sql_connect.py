import pymssql

conn = None
try:
    conn = pymssql.connect('10.211.55.2', 'sa', 'Wht157/@', 'OneIM')
except pymssql.InterfaceError:
    print('interface error')

cursor = conn.cursor()
sql = 'select * from accproduct'
rows = None
try:
    cursor.execute(sql)
    rows = cursor.fetchall()
except pymssql.Error:
    print('execute error')
print(f'Row number is {len(rows)}')

conn.close()
