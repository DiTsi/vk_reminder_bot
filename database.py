
import psycopg2
from pprint import pprint

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
    cur.execute("SELECT * FROM " + tablename + " WHERE num=" + str(num) +";")
    list = cur.fetchall()

    cur.close()
    conn.close()

    if len(list) > 1:
        print('More then one row with this ID')
        id0, num0, str0 = list[0]
        return {"id": id, "num": num0, "data": str0}
    elif len(list) == 1:
        id0, num0, str0 = list[0]
        return {"id": id, "num": num0, "data": str0}
        # return list
    else:
        return {}


def db_replace(dbname, tablename, number, oldvalue, newvalue):
    conn = psycopg2.connect("dbname='" + str(dbname) + "' user='" + dbuser + "' host='localhost'")
    cur = conn.cursor()
    cur.execute("UPDATE test SET data = '" + str(newvalue) + "' WHERE data = '" + str(oldvalue) + "';")
    # cur.execute("SELECT * FROM " + 'test' + ";")
    conn.commit()
    cur.close()
    conn.close()


def main():
    # db_add('vk_reminder', 'test', 1923, 'kukuepta')
    db_show('vk_reminder', "test")

    db_search('vk_reminder', "test", 1923)
    db_show('vk_reminder', "test")
    res = db_search('vk_reminder', "test", 1923)
    # res["num"]
    db_replace('vk_reminder', "test", res["num"], res["data"], "hello")
    db_show('vk_reminder', "test")
    #
    # print(list[0])
    # id, num, string0 = list[0]
    # str0 = 'qwerty'




    # b = db_show('vk_reminder', "test")

    exit(0)


main()
