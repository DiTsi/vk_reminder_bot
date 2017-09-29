import psycopg2
# from pprint import pprint


# DATABASE
dbname = <db_name>
password = <password>
host = <host>
tablename = 'tzone'
dbuser = <db_user>
first_col_name = 'user_id'
second_col_name = 'tz'



def db_create():
    try:
        conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
    except Exception as err:
        print("Connection error: {}".format(err))
        exit(1)
    else:
        cur = conn.cursor()
        cur.execute("CREATE TABLE " + tablename + " (id serial PRIMARY KEY, " + first_col_name + " integer, " + second_col_name + " integer);")
        conn.commit()
        cur.close()
        conn.close()


def db_show():
    conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + tablename + ";")
    full_list = cur.fetchall()
    print("[")
    for list_element in full_list:
        print(str(list_element))
    print("]")
    cur.close()
    conn.close()


def db_add(num, data):

    search_result = db_search(str(num))

    if not search_result:
        try:
            conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
            cur = conn.cursor()
            cur.execute("INSERT INTO " + tablename + " (" + first_col_name + ", " + second_col_name + ") VALUES (%s, %s)", (str(num), str(data)))
            cur.execute("SELECT * FROM " + tablename + ";")
            # print(cur.fetchone())
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            print('Can\'t add User in database')
        else:
            print('User was successfully added')
    else:
        try:
            db_replace(num, search_result['data'], data)
        except Exception:
            print('Can\'t change GMT in database')
        else:
            print('User GMT was changed in database')


def db_search(num):
    conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + tablename + " WHERE " + first_col_name + "=" + str(num) +";")
    list = cur.fetchall()

    cur.close()
    conn.close()

    if len(list) > 1:
        print('More then one row with this ID')
        num0, str0 = list[0]
        return {"num": num0, "data": str0}
    elif len(list) == 1:
        num0, str0 = list[0]
        return {"num": num0, "data": str0}
        # return list
    else:
        return {}


def db_replace(number, oldvalue, newvalue):
    conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
    cur = conn.cursor()
    # cur.execute("SELECT * FROM " + tablename + " WHERE " + first_col_name + " = " + str(number) + ";")
    # print('fetchall = ' + str(cur.fetchall()))
    cur.execute("UPDATE " + tablename + " SET " + second_col_name + " = '" + str(newvalue) + "' WHERE " + first_col_name + " = '" + str(number) + "';")
    # cur.execute("SELECT * FROM " + 'test' + ";")
    conn.commit()
    cur.close()
    conn.close()


def db_delete(number):
    conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=password)
    cur = conn.cursor()
    cur.execute("DELETE FROM " + tablename + " WHERE " + first_col_name + " = " + str(number) + ";")
    # cur.execute("SELECT * FROM " + 'test' + ";")
    conn.commit()
    cur.close()
    conn.close()
