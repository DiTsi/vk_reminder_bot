import psycopg2
# import psycopg2.extras

# try:
conn = psycopg2.connect("dbname='vk_reminder' user=<db_user> host='localhost'")
# except psycopg2.Error as err:
#     print("Connection error: {}".format(err))

# sql = "SELECT * FROM vk_reminder LIMIT 3"

# try:
cur = conn.cursor()
# cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (200, "ab'def"))
# cur.execute("SELECT user_id FROM vk_reminder ORDER BY Name LIMIT 3")
cur.execute("SELECT * FROM test;")
id = cur.fetchone()[0]
list = cur.fetchall()
# print(i for i in list)
for i in list:
    print(str(i))

conn.commit()

cur.close()
conn.close()
# result = cur.fetchall()
# print(result)

    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # by column name
    # cur.execute(sql)
    # data = cur.fetchall()
# except psycopg2.Error as err:
#     print("Query error: {}".format(err))

# print(data)