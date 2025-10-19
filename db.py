import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    if params is None:
        params=[]
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    last_id = result.lastrowid
    con.close()
    return last_id

def last_insert_id():
    return g.last_insert_id

def query(sql, params=None, return_one=False):
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    if not result:
        return None if return_one else  []
    return result[0] if return_one else result