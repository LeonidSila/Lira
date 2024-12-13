import sqlite3
import sys

conn = None
cursor = None
def creat_teble():
    global conn
    global cursor
    conn = sqlite3.connect('lira_db.sql')
    # conn = sqlite3.connect('lira_db — copy.sql')
    cursor = conn.cursor()
    
