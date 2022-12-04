#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import sys
from datetime import datetime, timedelta
from dateutil import rrule
import re


#Initialize the app from Flask
app = Flask(__name__)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='flight_sim',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor,
					   port=3306
					   )
import register
import account
from helperFuncs import *

#Define a route to hello function
@app.route('/')
def root():
	# print("test", file=sys.stdout)
	cursor = conn.cursor()
	
	flights_query = 'SELECT * from flight'
	cursor.execute(flights_query)
	flights = cursor.fetchall()

	# airports_query = 'SELECT * from airport'
	# cursor.execute(airports_query)
	# airports = cursor.fetchall()
	# print(airports)
	airports = get_airports()
	cursor.close()
	# print(flights, file=sys.stdout)
	
	return render_template('index.html', flights=flights, airports=airports)

@app.route('/flights', methods=['GET', 'POST'])
def flights():
	# non-logged in use case for search
	airport = request.form['airport']
	departure_date = request.form['depart']
	return_date = request.form['return']
	print(return_date)
	cursor = conn.cursor()

	if not return_date:
		query = 'SELECT * from flight where departure_date = %s and depart_from = %s'
		cursor.execute(query, (departure_date, airport))

	else:
		query = 'SELECT * from flight where departure_date = %s and depart_from = %s and arrive_at in (Select depart_from from flight where departure_date = %s);' 
		cursor.execute(query, (departure_date, airport, return_date))	

	data = cursor.fetchall()	
	return render_template('index.html', flights=data)

@app.route('/pastFlights', methods=["GET"])
def past_flights():

	# This is the customer version, the regular version is just query = 'SELECT * from flight natural join ticket where flight.departure_date < CAST(CURRENT_DATE() as Date) and email = %s;'
	# check the session for the right email, for now skipping that 
	email = "totallylegit@nyu.edu"
	cursor = conn.cursor()
	# query = 'SELECT * from flight AS C, ticket AS D where C.airline_name = D.airline_name and C.unique_airplane_num = D.unique_airplane_num and C.flight_number = D.flight_number and C.departure_date = D.departure_date and C.departure_time = D.departure_time and D.email = %s and C.departure_date < CAST(CURRENT_DATE() AS Date);'
	# need to double check this query
	query = "SELECT * from flight natural join ticket as C left join ratings on (ratings.airline_name = C.airline_name and ratings.email = C.email and ratings.unique_airplane_num = C.unique_airplane_num and ratings.flight_number = C.flight_number and ratings.departure_date = C.departure_date and ratings.departure_time = C.departure_time) where flight.departure_date < CAST(CURRENT_DATE() as Date) and C.email = %s"
	cursor.execute(query, (email))

	# need to do another to check tickets
	# query = 'SELECT '
	data = cursor.fetchall() 
	print(data)
	return render_template('index.html', flights=data, hide_header=True, past_flights=True)

@app.route('/futureFlights', methods=["GET"])
def future_flights():

	# noncustomer version is just query = 'SELECT * from flight natural join ticket where flight.departure_date >= CAST(CURRENT_DATE() as Date) and email = %s;'
	# also the customer version, need to check that  
	email = "notlegit@nyu.edu"
	cursor = conn.cursor()
	# actually, as a private business, I don't care if you buy multiple tickets, that's your right, maybe give one to a friend 
	# add email check here too
	query = 'SELECT * from flight natural join ticket where flight.departure_date >= CAST(CURRENT_DATE() as Date) and email = %s;'
		
	cursor.execute(query, (email))
	data = cursor.fetchall()
	return render_template('index.html', flights=data, hide_header=True)

def calculate_spending(start_date, end_date):
	table_info = []
	total_spending = 0
	for full_date in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
		date, time = str(full_date).split()
		year, month, day = date.split("-")
		# print(day)
		# print(month)
		# print(year)
		email = "totallylegit@nyu.edu"
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

@app.route('/spending')
# @role_required("Customer")
def spending_default():
	# get the dates properly later
	start_date = datetime(2022, 6, 3)
	end_date = datetime(2022, 12, 3)
	table_info, total_spending = calculate_spending(start_date, end_date)
	print(table_info)
	print(total_spending)

	return render_template('spending.html', table_info=table_info, total=total_spending)

@app.route('/spend_specify', methods=["POST"])
def spending_specify():
	start_year, start_month, start_day  = request.form['start'].split("-") 
	start_date = datetime(int(start_year), int(start_month), int(start_day))
	end_year, end_month, end_day  = request.form['end'].split("-") 
	end_date = datetime(int(end_year), int(end_month), int(end_day))
	table_info, total_spending = calculate_spending(start_date, end_date)
	return render_template('spending.html', table_info=table_info, total=total_spending)

@app.route('/comment', methods=["POST"])
def comment():
	rating = request.form['rating']
	comment = request.form['comment']
	info = request.form['sendover']

	splitter = re.sub('[(){}\'"]', '', info).split(",")
	holder = {}
	i = 0
	while i < len(splitter):
		if "datetime.date" in splitter[i]:
			key, value = splitter[i].split(":")
			key = key.strip()
			value = value[14:]
			value += "-" + splitter[i + 1] + "-" + splitter[i + 2]
			holder[key[0:14]] = datetime.strptime(value.replace(" ", ""), '%Y-%m-%d')
			i += 3
		else:
			key, value = splitter[i].replace(" ", "").split(':')
			key = key.strip()
			if key == "departure_time":
				holder[key] = timedelta(seconds=int(value[26:]))
			else:
				holder[key] = value
			i += 1

	print(holder)
	email = holder['email']
	airline_name = holder['airline_name']
	unique_airplane_num = holder['unique_airplane_num']
	flight_number = holder['flight_number']
	departure_date = holder['departure_date']
	departure_time = holder['departure_time']

	cursor = conn.cursor()
	query = 'INSERT into ratings Values (%s, %s, %s, %s, %s, %s, %s, %s)'
	
	cursor.execute(query, (email, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, rating, comment))	
	conn.commit()
	cursor.close()
	return render_template('submitted.html')
	# redirect("submitted.html")

# @app.route('/home')
# def customer():
	# return render_template('Customers/customer.html')

# @app.route('/flightsearch')
# def flightsearch():
	# query = "SELECT * from flight where depart_from = %s, arrive_at = %s, departure_date=%s"
	# return 

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)


# @app.route('/home')
# def home():
#     username = session['username']
#     cursor = conn.cursor()
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, (username))
#     data1 = cursor.fetchall() 
#     # for each in data1:
#         # print(each['blog_post'])
#     cursor.close()
#     return render_template('home.html', username=username, posts=data1)

		
# @app.route('/post', methods=['GET', 'POST'])
# def post():
# 	username = session['username']
# 	cursor = conn.cursor()
# 	blog = request.form['blog']
# 	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
# 	cursor.execute(query, (blog, username))
# 	conn.commit()
# 	cursor.close()
# 	return redirect(url_for('home'))