from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *
from functools import wraps
from datetime import datetime
import random
from datetime import datetime, timedelta, date

@app.route('/myaccount')
def myaccount():
	if "email" in session:
		return redirect('/Customers/customer')
	elif "username" in session:
		return redirect('/Staff/staff')

# Customer Use Cases
@app.route('/Customers/customer')
@role_required("Customer")
def customer():
    return render_template("Customers/customer.html")

#Define a route to hello function
@app.route('/')
def root():
    # should only show future flights for which the traveler has purchased tickets from - also shouldn't manage tickets (canceling flights) here, should be done on the ticket page
    airports = get_airports()
    if 'email' in session: # check if a customer is logged in 
        email = session['email']
        cursor = conn.cursor()
        query = 'SELECT distinct F.airline_name, F.unique_airplane_num, F.flight_number, F.departure_date, F.departure_time, F.arrival_date, F.arrival_time, F.base_price, F.status_flight, F.roundtrip, F.depart_from, F.arrive_at from flight as F, ticket as T where F.airline_name = T.airline_name and F.unique_airplane_num = T.unique_airplane_num and F.flight_number = T.flight_number and F.departure_date = T.departure_date and F.departure_time = T.departure_time and email = %s'
        cursor.execute(query, (email)) 
        flights = cursor.fetchall()      
        flights = add_time_difference(flights)
        return render_template('index.html', flights=flights, airports=airports, book_flights=True)
    else:
        flights = getFutureFlights()
        return render_template('index.html', flights=flights, airports=airports)

@app.route('/pastFlights', methods=["GET"])
@role_required('Customer')
def pastFlights():
    email = session['email']
    cursor = conn.cursor()
    query = "SELECT * from flight natural join ticket as C left join ratings on (ratings.airline_name = C.airline_name and ratings.email = C.email and ratings.unique_airplane_num = C.unique_airplane_num and ratings.flight_number = C.flight_number and ratings.departure_date = C.departure_date and ratings.departure_time = C.departure_time) where flight.departure_date < CAST(CURRENT_DATE() as Date) and C.email = %s"
    cursor.execute(query, (email))
    
    flights = cursor.fetchall() 
    flights = add_time_difference(flights)

    return render_template('index.html', flights=flights, hide_header=True, past_flights=True) # this doesn't seem to work ??????

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
	return render_template('submitted.html')


@app.route('/flights', methods=['GET', 'POST'])
def flights():
    airport = request.form['airport']
    departure_date = request.form['depart']
    return_date = request.form['return']
    show_book_button = False

    if 'email' in session:
        show_book_button = True

    cursor = conn.cursor()
    if not return_date:
        query = 'SELECT * from flight where departure_date = %s and depart_from = %s'
        cursor.execute(query, (departure_date, airport))
    else:
        query = 'SELECT * from flight where departure_date = %s and depart_from = %s and arrive_at in (Select depart_from from flight where departure_date = %s);' 
        cursor.execute(query, (departure_date, airport, return_date))	

    data = cursor.fetchall()	
    return render_template('index.html', flights=data, hide_header=True, book_flights=show_book_button, re_search=True)

# Ticket management
@app.route('/getTickets', methods=["GET", "POST"])
@role_required('Customer')
def get_tickets():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * from ticket where email = %s'
    
    # need to add 24 hour requirement still
    cursor.execute(query, (email))
    tickets = cursor.fetchall()

    for ticket in tickets:
        departure = datetime.strptime(str(ticket["departure_date"])+" "+str(ticket["departure_time"]),  '%Y-%m-%d %H:%M:%S')
        current = departure - datetime.now() 
        if current > timedelta(days=1):
            ticket["can_cancel"] = True
        else:
            ticket["can_cancel"] = False
        # print(current)
        # arr = datetime.strptime(str(flight["arrival_date"])+" "+str(flight["arrival_time"]),  '%Y-%m-%d %H:%M:%S')
        # flight["total_time"] = str(arr - dep)

    return render_template('index.html', flights=tickets, hide_header=True, view_tickets=True)

# Buying a ticket
@app.route('/buyTicket', methods=["GET", "POST"])
def buyTicket():
    cursor = conn.cursor()
    ticket_id = random.randrange(1, 10**10)
    query = 'SELECT * from ticket where ticket.ticket_id = %s'
    cursor.execute(query, (ticket_id))	
    check = cursor.fetchone()
    error_count = 0

    # Verifies that the ticket_id is unique, if it takes too long, then give up 	
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

    # flight verification
    query = 'SELECT * from flight where airline_name = %s and unique_airplane_num = %s and flight_number = %s and departure_date = %s and departure_time = %s'
    cursor.execute(query, (airline_name, unique_airplane_num, flight_number, departure_date, departure_time)) 
    data = cursor.fetchone()

    if (data):  
        # get number of seats to seats
        query = 'SELECT num_of_seats from airplane where airline_name = %s and unique_airplane_num = %s'
        cursor.execute(query, (airline_name, unique_airplane_num))

        total_seats = cursor.fetchone()['num_of_seats']
        # print("Test")
        print(total_seats)
        # count number of tickets 
        query = 'SELECT count(*) from ticket where airline_name = %s and unique_airplane_num = %s and flight_number = %s and departure_date = %s and departure_time = %s'
        cursor.execute(query, (airline_name, unique_airplane_num, flight_number, departure_date, departure_time)) 
        count_tickets = cursor.fetchone()['count(*)']

        if count_tickets // total_seats > 0.6:
            base_price *= 1.25

        query = 'INSERT into ticket Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (ticket_id, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, card_type, card_number, name_on_card, expiration, base_price, email, purchase_date, purchase_time))
        conn.commit()
        cursor.close()

    return render_template('submitted.html')

@app.route('/cancelTicket', methods=["GET", "POST"])
def cancelTicket():
    cursor = conn.cursor()
    email = session['email']
    ticket_id = int(float(request.form['ticket_id']))

    #check that the ticket_id is in your email so you can't delete someone elses ticket
    query = 'SELECT * from ticket where email = %s and ticket_id = %s'
    cursor.execute(query, (email, ticket_id))
    data = cursor.fetchone()
    print(ticket_id)

    if (data):
        query = 'DELETE from ticket where ticket.ticket_id = %s' # only works temporarily? a bit strange 
        cursor.execute(query, (ticket_id))
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
    email = session['email']
    start_year, start_month, start_day  = request.form['start'].split("-") 
    start_date = datetime(int(start_year), int(start_month), int(start_day))
    end_year, end_month, end_day  = request.form['end'].split("-") 
    end_date = datetime(int(end_year), int(end_month), int(end_day))

    table_info, total_spending = calculate_spending(email, start_date, end_date)
    return render_template('spending.html', table_info=table_info, total=total_spending)

# @app.route('/Staff/createflight', methods=['POST'])
# @role_required("Staff")
# def createflight():
#     airport = request.form['airport'];
#     # airport = request.form[]

