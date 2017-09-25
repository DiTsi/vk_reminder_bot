
import psycopg2

# dbname = <db_name>
dbuser = <db_user>


def db_show(dbname, tablename):
    conn = psycopg2.connect("dbname='" + dbname + "' user='" + dbuser + "' host='localhost'")
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + tablename + ";")
    full_list = cur.fetchall()
    for list_element in full_list:
        print(str(list_element))
    cur.close()
    conn.close()


def db_add(dbname, tablename, num, data):
    conn = psycopg2.connect("dbname='" + dbname + "' user='" + dbuser + "' host='localhost'")
    cur = conn.cursor()
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (num, data))
    cur.execute("SELECT * FROM " + tablename + ";")
    print(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()


def db_search(dbname, tablename, num):
    conn = psycopg2.connect("dbname='" + dbname + "' user='" + dbuser + "' host='localhost'")
    cur = conn.cursor()
    # cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (num, data))
    cur.execute("SELECT " + str(num) + " FROM " + tablename + ";")
    print(cur.fetchall())
    # conn.commit()
    cur.close()
    conn.close()

    return


def main():
    db_add('vk_reminder', 'test', 34, 'kukuepta')
    db_show('vk_reminder', "test")
    db_search('vk_reminder', "test", 34)


main()
