from __main__ import conn
import pymysql.cursors
import hashlib
import sys
from dateutil import rrule

def get_airports():
	cursor = conn.cursor()
	airports_query = 'SELECT * from airport'
	cursor.execute(airports_query)
	airports = cursor.fetchall()
	# print(airports)
	return airports

def calculate_spending(email, start_date, end_date):
	table_info = []
	total_spending = 0
	for full_date in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
		date, time = str(full_date).split()
		year, month, day = date.split("-")
		cursor = conn.cursor()
		query = 'select sum(sold_price) as monthly_spending from ticket where email = %s and MONTH(purchase_date) = %s and YEAR(purchase_date) = %s group by email;'
		cursor.execute(query, (email, str(month), str(year)))
		spending = cursor.fetchone() 
		# print(spending)
		if spending:
			total_spending += spending["monthly_spending"] 
			table_info.append((date, spending["monthly_spending"])) 
		else:
			table_info.append((date, 0))

	return table_info, total_spending