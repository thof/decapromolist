import MySQLdb as mdb

con = mdb.connect('sohost.pl', 'so819_demos', '19odra22', 'so819_demos')
cur = con.cursor(mdb.cursors.DictCursor)
cur.execute('SELECT * FROM ep_buttons')
test = cur.fetchall()
print(test)