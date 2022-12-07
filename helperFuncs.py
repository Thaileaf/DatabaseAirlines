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

def add_time_difference(flights):
    for flight in flights:
        dep = datetime.datetime.strptime(str(flight["departure_date"])+" "+str(flight["departure_time"]),  '%Y-%m-%d %H:%M:%S')
        arr = datetime.datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
        flight["total_time"] = str(arr - dep)

    return flights

def getFutureFlights(airline = None):
    cursor = conn.cursor()
    if(airline):
        flights_query = 'SELECT * FROM flight WHERE flight.departure_date >= CAST(CURRENT_DATE() as Date) AND airline_name = %s'
        cursor.execute(flights_query, [airline])
        flights = cursor.fetchall()
        cursor.close()

        # for flight in flights: 
        # 	dep = datetime.datetime.strptime(str(flight["departure_date"])+" "+str(flight["departure_time"]),  '%Y-%m-%d %H:%M:%S')
        # 	arr = datetime.datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
        # 	flight["total_time"] = str(arr-dep)
        # return flights
        return add_time_difference(flights)

    else:
        flights_query = 'SELECT * from flight where flight.departure_date >= CAST(CURRENT_DATE() as Date)'
        cursor.execute(flights_query)
        flights = cursor.fetchall()
        cursor.close()
        # for flight in flights: 
        # 	dep = datetime.datetime.strptime(str(flight["departure_date"])+" "+str(flight["departure_time"]),  '%Y-%m-%d %H:%M:%S')
        # 	arr = datetime.datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
        # 	flight["total_time"] = str(arr-dep)
        # return flights

        return add_time_difference(flights)

def findFlight(airline, flight_num):
    cursor = conn.cursor() 
    query = 'SELECT * FROM flight WHERE airline_name = %s and flight_number = %s'
    cursor.execute(query, (airline, flight_num))
    return cursor.fetchall()

def calculate_spending(email, start_date, end_date):
    table_info = []
    total_spending = 0
    # for full_date in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
    # 	date, time = str(full_date).split()
    # 	year, month, day = date.split("-")
    # 	cursor = conn.cursor()
    # 	query = 'select sum(sold_price) as monthly_spending from ticket where email = %s and MONTH(purchase_date) = %s and YEAR(purchase_date) = %s group by email;'
    # 	cursor.execute(query, (email, str(month), str(year)))
    # 	spending = cursor.fetchone() 
    # 	# print(spending)
    # 	if spending:
    # 		total_spending += spending["monthly_spending"] 
    # 		table_info.append((date, spending["monthly_spending"])) 
    # 	else:
    # 		table_info.append((date, 0))
    
    data = calculate_by_month(start_date, end_date, "sum(sold_price)", email)
    # cursor = conn.cursor()
    # query = 'SELECT sum(sold_price) as tot, DATE_FORMAT(departure_date, "%Y-%m") AS year_and_month FROM (SELECT * FROM ticket WHERE departure_date > %s AND departure_date < %s AND airline_name like %s and email = %s) as TABLE1 GROUP BY year_and_month DESC;'''
    # cursor.execute(query, (departure))
    total_spending = sum([i["tot"] for i in data])

    return data, total_spending

def calculate_by_month(startDate, endDate, select, email="%", airline_name="%"):
    # Returns data of selected columns in Ticket
    # if not endDate and not startDate:
    #     endDate = datetime.date.today().strftime("%y-%m-%d")
    # print("1")
    query = 'SELECT ' + select + ''' as tot, DATE_FORMAT(departure_date, "%%Y-%%m") AS year_and_month FROM (SELECT * FROM ticket WHERE departure_date > %s AND 
    departure_date < %s AND airline_name like %s and email like %s) as TABLE1 GROUP BY year_and_month DESC;'''

    # print(query
    cursor = conn.cursor()
    cursor.execute(query, (startDate, endDate, airline_name, email))
    # print("2")


    return cursor.fetchall()

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


def getComments( aName = None, fNum = None, dTime = None, dDate = None, aNum = None, customer = None): 
    
    q1 = "airline_name = %s"
    q2 = "flight_number = %s"
    q3 = "departure_time = %s"
    q4 = "departure_date = %s"
    q5 = "unique_airplane_num = %s"
    q6 = "email = %s"
    query = "SELECT * FROM ratings WHERE "
    values = []
    fquery= []
    if(aName): 
        fquery.append(q1)
        values.append(aName)
    if(fNum): 
        fquery.append(q2)
        values.append(fNum)
    if(dTime): 
        fquery.append(q3)
        values.append(dTime)
    if(dDate):
        fquery.append(q4)
        values.append(dDate)
    if(aNum): 
        fquery.append(q5)
        values.append(aNum)
    if(customer): 
        fquery.append(q6)
        values.append(customer)
    if(len(values) == 0): 
        return 
    fquery = " AND ".join(fquery)
    cursor = conn.cursor() 
    cursor.execute(query + " " +fquery, values)
    res = cursor.fetchall() 
    return res

def searchFlight(dep = None, arr = None, arrCity = None, depCity = None, start = None, end = None, depCountry = None, arrCountry = None ):
	findQuery = "SELECT * FROM flight WHERE"
	cursor = conn.cursor()
	conditionals = []
	conditionals_val = []
	airports = get_airports()
	
	arrPort = set()
	depPort = set()
	for port in airports: 
		arrPort.add(port["name"])
		depPort.add(port["name"])
	if(dep): 
		depPort = depPort.intersection({dep})
	if(arr): 
		arrPort = arrPort.intersection({arr})
	if(arrCity or arrCountry): 
		q1 = "SELECT * FROM airport WHERE "
		args = []
		args_con = []
		if(arrCity): 
			args_con.append(" city = %s ")
			args.append(arrCity)
		if(arrCountry): 
			args_con.append(" country = %s ")
			args.append(arrCountry)
		q1 += " AND ".join(args_con)
		cursor.execute(q1,args)
		hold = cursor.fetchall()
		a = set()
		for port in hold: 
			a.add(port["name"])
		arrPort =arrPort.intersection(a)
	if(depCity or depCountry): 
		q1 = "SELECT * FROM airport WHERE "
		args = []
		args_con = []
		if(depCity): 
			args_con.append(" city = %s ")
			args.append(depCity)
		if(depCountry): 
			args_con.append(" country = %s ")
			args.append(depCountry)
		q1 += " AND ".join(args_con)
		cursor.execute(q1, args)
		hold = cursor.fetchall()
		d = set()
		for port in hold: 
			d.add(port["name"])
		depPort = depPort.intersection(d)
	if(start): 
		conditionals_val.append(start)
		conditionals.append("departure_date > %s")
	if(end): 
		conditionals_val.append(end)
		conditionals.append("departure_date < %s")
	
	if(len(conditionals) == 0): 
		findQuery = "SELECT * FROM flight WHERE departure_date > CAST( CURRENT_DATE() AS Date) AND departure_date < CAST( CURRENT_DATE() AS Date) +30"
	conditionals = " AND ".join(conditionals)
	findQuery += " " 
	findQuery += conditionals
	arrPort = tuple(arrPort)
	depPort = tuple(depPort)
	findQuery += " AND arrive_at in %s"
	findQuery += " AND depart_from in %s"
	if(len(arrPort) == 0 or len(depPort) == 0): 
		return [] 
	# print(conditionals_val+[arrPort,depPort])
	# print(findQuery)
	cursor.execute(findQuery, conditionals_val+[arrPort,depPort])
	flights = cursor.fetchall()

	return flights

def findCustomersForFlight(flight): 
	query = "SELECT email, ticket_ID FROM Ticket WHERE airline_name = %s AND unique_airplane_num = %s AND flight_number = %s AND departure_date = %s AND departure_time = %s"
	args = [flight["airline_name"], flight["unique_airplane_num"], flight["flight_number"], flight['departure_date'], flight["departure_time"]]
	cursor = conn.cursor() 
	cursor.execute(query,args)
	customers = cursor.fetchall() 
	return customers

	

