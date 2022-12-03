from __main__ import conn
import pymysql.cursors
import hashlib
import sys
def get_airports():
	cursor = conn.cursor()
	airports_query = 'SELECT * from airport'
	cursor.execute(airports_query)
	airports = cursor.fetchall()
	# print(airports)
	return airports