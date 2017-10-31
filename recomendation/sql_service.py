#!/usr/bin/python
import MySQLdb

def connect():
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="BookCrossing")
    return db

# you must create a Cursor object. It will let
#  you execute all the queries you need
# db = connect()
# cur = db.cursor()

# Use all the SQL you like
# cur.execute("SELECT * FROM `BX-Book-Ratings`")

# print all the first cell of all the rows
# for row in cur.fetchall():
#     print row[1], row[2]

# db.close()
