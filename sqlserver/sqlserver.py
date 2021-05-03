# -*- coding: utf-8 -*-
import pyodbc

def login():
    # インスタンス
    instance = "boogie\SQLEXPRESS"

    # ユーザー
    user = "analysis"

    #パスワード
    pasword = "analysis"

    #DB
    db = "Analysis"

    connection = "DRIVER={SQL Server};SERVER=" + instance + ";uid=" + user + \
                 ";pwd=" + pasword + ";DATABASE=" + db


    return pyodbc.connect(connection)

if __name__ == '__main__':
    con = login()
    cursor = con.cursor()
    cursor.execute("select * from test")
    rows = cursor.fetchall()
    cursor.close()
    for r in rows:
        print(r[0], r[1])
