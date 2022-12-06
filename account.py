from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *
from functools import wraps
from datetime import datetime
import random

@app.route('/myaccount')
def myaccount():
	if "email" in session:
		return redirect('/Customers/customer')
	elif "username" in session:
		return redirect('/Staff/staff')



@app.route('/Staff/staff')
@role_required("Staff")
def staff():
    airports = get_airports()
    return render_template("Staff/staff.html", airports = airports);


# Customer Use Cases

@app.route('/Customers/customer')
# @role_required("Customer") # removed this for testing
def customer():
    return render_template("Customers/customer.html")

@app.route('/pastFlights', methods=["GET"])
@role_required('Customer')
def pastFlights():
    email = session['email']
    # print(email)
	# email = "totallylegit@nyu.edu"
    cursor = conn.cursor()
    query = "SELECT * from flight natural join ticket as C left join ratings on (ratings.airline_name = C.airline_name and ratings.email = C.email and ratings.unique_airplane_num = C.unique_airplane_num and ratings.flight_number = C.flight_number and ratings.departure_date = C.departure_date and ratings.departure_time = C.departure_time) where flight.departure_date < CAST(CURRENT_DATE() as Date) and C.email = %s"
    cursor.execute(query, (email))

    data = cursor.fetchall() 
    # print(data)
    return render_template('index.html', flights=data, hide_header=True, past_flights=True, view_comments=True) # this doesn't seem to work ??????

@app.route('/comment', methods=["POST"])
@role_required('Customer')
def comment():
	email = session['email']
	rating = request.form['rating']
	comment = request.form['comment']
	airline_name = str(request.form['airline_name'])
	unique_airplane_num = int(float(request.form['unique_airplane_num']))
	flight_number = int(float(request.form['flight_number']))
	departure_date = str(request.form['departure_date'])
	departure_time = str(request.form['departure_time'])

    # need to check for duplicate entry still here
	cursor = conn.cursor()
	query = 'INSERT into ratings Values (%s, %s, %s, %s, %s, %s, %s, %s)'
	
	cursor.execute(query, (email, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, rating, comment))	
	conn.commit()
	cursor.close()
	return render_template('submitted.html', view_comments=True)

# Future flights, maybe don't want tickets actually (since ) natural join ticket
@app.route('/futureFlights', methods=["GET"])
@role_required('Customer')
def future_flights():
	email = session['email']
	cursor = conn.cursor()
	# add email check here tooand email = %s  flight.
	query = 'SELECT * from flight where departure_date >= CAST(CURRENT_DATE() as Date)'
	cursor.execute(query) #, (email)
	data = cursor.fetchall()
	return render_template('index.html', flights=data, hide_header=True, book_flights=True, view_tickets=False)

# Ticket management
@app.route('/getTickets', methods=["GET", "POST"])
@role_required('Customer')
def get_tickets():
	email = session['email']
	cursor = conn.cursor()
	query = 'SELECT * from ticket where email = %s'
	
	cursor.execute(query, (email))
	data = cursor.fetchall()
	return render_template('index.html', flights=data, hide_header=True, view_tickets=True)

@app.route('/buyTicket', methods=["GET", "POST"])
def buyTicket():
	cursor = conn.cursor()

	ticket_id = random.randrange(1, 10**10)
	query = 'SELECT * from ticket where ticket.ticket_id = %s'
	cursor.execute(query, (ticket_id))	
	check = cursor.fetchone()
	error_count = 0

	# verifies that the ticket_id is unique, if it takes too long, then give up 	
	while check and error_count < 50:
		error_count += 1
		ticket_id = '{:10}'.format(random.randrange(1, 10**10))
		cursor.execute(query, (ticket_id))	
		check = cursor.fetchone()
	if check:
		raise RuntimeError("Unable to generate ticket_id")

	purchase_date = date.today()
	purchase_time = datetime.now().strftime("%H:%M:%S")
	email = session['email']

	airline_name = str(request.form['airline_name'])
	unique_airplane_num = int(float(request.form['unique_airplane_num']))
	flight_number = int(float(request.form['flight_number']))
	departure_date = str(request.form['departure_date'])
	departure_time = str(request.form['departure_time'])
	card_type = request.form['drone']
	card_number = int(request.form['card_number'])
	name_on_card = request.form['name_on_card']
	expiration = request.form['expiration'] + "-01" #adding extra day to conform with db
	base_price = int(float(request.form['base_price']))

	query = 'SELECT * from flight where airline_name = %s and unique_airplane_num = %s and flight_number = %s and departure_date = %s and departure_time = %s'
	cursor.execute(query, (airline_name, unique_airplane_num, flight_number, departure_date, departure_time)) #departure_date, departure_date
	data = cursor.fetchone()
	# print(data)
	if (data):
		# need to change base price depending on how many people are on the plane, can have fixed number of seats but if 60% of the capacity is full (booked/reserved), then extra 25% will be added to min/base price
		sold_price = base_price + 10
		query = 'INSERT into ticket Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(query, (ticket_id, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, card_type, card_number, name_on_card, expiration, sold_price, email, purchase_date, purchase_time))
		conn.commit()
		cursor.close()

	return render_template('submitted.html')

@app.route('/spending')
@role_required("Customer")
def spending_default():
    email = session['email']
    start_date = datetime(2022, 6, 3)
    end_date = datetime(2022, 12, 3)
    table_info, total_spending = calculate_spending(email, start_date, end_date)
    return render_template('spending.html', table_info=table_info, total=total_spending)

@app.route('/spendSpecify', methods=["POST"])
@role_required("Customer")
def spending_specify():
	start_year, start_month, start_day  = request.form['start'].split("-") 
	start_date = datetime(int(start_year), int(start_month), int(start_day))
	end_year, end_month, end_day  = request.form['end'].split("-") 
	end_date = datetime(int(end_year), int(end_month), int(end_day))

	table_info, total_spending = calculate_spending(start_date, end_date)
	return render_template('spending.html', table_info=table_info, total=total_spending)


# @app.route('/Staff/createflight', methods=['POST'])
# @role_required("Staff")
# def createflight():
#     airport = request.form['airport'];
#     # airport = request.form[]

