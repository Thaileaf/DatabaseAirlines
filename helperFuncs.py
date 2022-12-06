from __main__ import conn, session, redirect
import pymysql.cursors
import hashlib
import sys
import datetime
from dateutil import rrule
from functools import wraps

# Decorator
# Used to ensure only correct users can access page
# Put under routes
def role_required(role):
    def decorator(func):
        @wraps(func)
        def check(*args, **kwargs):
            if role == "Customer" and "email" in session:
                return func(*args, **kwargs)
            elif role == "Staff" and "username" in session:
                return func(*args, **kwargs)
            else:
                return redirect("/login") # not authorized
        return check
    return decorator

def get_airports():
	cursor = conn.cursor()
	airports_query = 'SELECT * from airport'
	cursor.execute(airports_query)
	airports = cursor.fetchall()
	return airports

def getFutureFlights(airline = None):
	cursor = conn.cursor()
	if(airline):
		flights_query = 'SELECT * FROM flight WHERE flight.departure_date >= CAST(CURRENT_DATE() as Date) AND airline_name = %s'
		cursor.execute(flights_query, [airline])
		flights = cursor.fetchall()
		cursor.close()

		for flight in flights: 
			dep = datetime.datetime.strptime(str(flight["departure_date"])+" "+str(flight["departure_time"]),  '%Y-%m-%d %H:%M:%S')
			arr = datetime.datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
			flight["TotalTime"] = str(arr-dep)
		return flights
	else:
		flights_query = 'SELECT * from flight where flight.departure_date >= CAST(CURRENT_DATE() as Date)'
		cursor.execute(flights_query)
		flights = cursor.fetchall()
		cursor.close()
		for flight in flights: 
			dep = datetime.datetime.strptime(str(flight["departure_date"])+" "+str(flight["departure_time"]),  '%Y-%m-%d %H:%M:%S')
			arr = datetime.datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
			flight["TotalTime"] = str(arr-dep)
		return flights


def findFlight(airline, flight_num):
	cursor = conn.cursor() 
	query = 'SELECT * FROM flight WHERE airline_name = %s and flight_number = %s'
	cursor.execute(query, (airline, flight_num))
	return cursor.fetchall()

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

def getAirplanes(airline = None): 
    if(airline): 
        query = "SELECT unique_airplane_num FROM airplane where airline_name = %s"
        cursor = conn.cursor()
        cursor.execute(query,(airline))
        airplanes = cursor.fetchall() 
        return airplanes
    else: 
        query = "SELECT unique_airplane_num FROM airplane"
        cursor = conn.cursor()
        cursor.execute(query)
        airplanes = cursor.fetchall() 
        for plane in airplanes: 
            plane["unique_airplane_num"] = int(plane["unique_airplane_num"])
        return airplanes