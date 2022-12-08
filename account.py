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
        # storing all flights in one big session, the button can still have a few hidden inputs to match the flights
        flights = add_time_difference(flights)
        return render_template('index.html', flights=flights, airports=airports, book_flights=False)
    else:
        cursor = conn.cursor()
        query = 'SELECT * from flight'
        cursor.execute(query)
        flights = cursor.fetchall()      
        return render_template('index.html', flights=flights, airports=airports)

@app.route('/searchFlights', methods=['GET', 'POST'])
def flights():

    cursor = conn.cursor()
    query = 'SELECT * from flight'
    cursor.execute(query)
    flights = cursor.fetchall()
    flights = add_time_difference(flights)

    # putting all flights in a session
    for flight in flights:
        key = str(flight['airline_name']) + str(flight['unique_airplane_num']) + str(flight['flight_number']) + str(flight['departure_date']) + str(flight['departure_time'])
        session[key] = [
            flight['airline_name'], #0
            flight['unique_airplane_num'], #1
            flight['flight_number'], #2
            flight['departure_date'], #3
            str(flight['departure_time']), #4 
            str(flight['arrival_time']), #6 
            flight['base_price'], #7
            flight['status_flight'], #8 
            flight['depart_from'], #9
            flight['arrive_at']] #10
    

    arrival_airport = str(request.form['arrival_airport'])
    departure_airport = str(request.form['departure_airport'])
    departure_date = str(request.form['departure_date'])

    print(arrival_airport)

    try:
        roundtrip_date = request.form['roundtrip_date']
    except:
        roundtrip_date = None

    cursor = conn.cursor()        

    if not roundtrip_date:
        query = 'SELECT * from flight where departure_date = %s and depart_from = %s and arrive_at = %s'
        cursor.execute(query, (departure_date, departure_airport, arrival_airport))	
        data = cursor.fetchall()
        return render_template('index.html', flights=data, hide_header=True, book_flights=True)    

    else:
        query_to = 'SELECT * from flight where departure_date = %s and depart_from = %s and arrive_at = %s'
        cursor.execute(query_to, (departure_date, departure_airport, arrival_airport))
        data = cursor.fetchall()
        
        query_back = 'SELECT * from flight where departure_date = %s and depart_from = %s and arrive_at = %s'
        cursor.execute(query_back, (roundtrip_date, arrival_airport, departure_airport))
        data2 = cursor.fetchall()
        print(data2)
    
        return render_template('index.html', flights=data, flights2=data2, hide_header=True, book_flights=True)    


    # if departure_airport == "": departure_airport = None  
    # if departure_date == "": departure_date = None
    # if arrival_airport == "": arrival_airport = None
    # if arrival_date == "": arrival_date = None

    # query = 'SELECT * from flight where departure_date = %s and depart_from = %s' # , departure_date, departure_airport
    # cursor.execute(query, (session['roundtrip_date'], arrival_airport, departure_airport))
    # data = cursor.fetchall()
    # return render_template('index.html', flights=data, hide_header=True, book_flights=False, roundtrip_ticket_buy=True)    

    # try:
    #     roundtrip_date = request.form['roundtrip_date']
    #     session['roundtrip_date'] = roundtrip_date
    # except:
    #     session['roundtrip_date'] = None

    # if 'email' in session:
    #     data = userSearchFlight(departure_airport, arrival_airport, departure_city, arrival_city, departure_date, arrival_date, session['roundtrip_date'])
    #     if 'roundtrip_date' in session:
    #         return render_template('index.html', flights=data, hide_header=True, book_flights=True, roundtrip_book_search=True)    
    #         session['roundtrip_book_search'] = True
        

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

# Ticket management
@app.route('/getTickets', methods=["GET", "POST"])
@role_required('Customer')
def get_tickets():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * from ticket where email = %s'
    
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
@role_required('Customer')
def buyTicket():     
    airline_name = request.form['airline_name']
    unique_airplane_num = request.form['unique_airplane_num']
    flight_number = str(request.form['flight_number'])
    departure_date = str(request.form['departure_date'])
    departure_time = str(request.form['departure_time'])
    key = str(airline_name) + str(unique_airplane_num) + str(flight_number) + str(departure_date) + str(departure_time)       
    
    base_price = session[key][6]
    print(base_price)
    data = unique_flight(airline_name, unique_airplane_num, flight_number, departure_date, departure_time)
    cursor = conn.cursor()

    ticket_id = generate_ticket_id()
    purchase_date = date.today()
    purchase_time = datetime.now().strftime("%H:%M:%S")
    email = session['email']

    card_type = request.form['card_type']
    card_number = int(request.form['card_number'])
    name_on_card = request.form['name_on_card']
    expiration = request.form['expiration'] + "-01" #adding extra day to conform with db

    # departure_airport = session[key][9]
    # arrival_airport = session[key][10]
    
    if (data):  
        base_price = float(base_price)
        base_price = price_modify(airline_name, unique_airplane_num, flight_number, departure_date, departure_time, base_price)
        query = 'INSERT into ticket Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (ticket_id, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, card_type, card_number, 
        name_on_card, expiration, base_price, email, purchase_date, purchase_time))
        print("made it here")
        conn.commit()

    # ticket_id = generate_ticket_id()
    # purchase_date = date.today()
    # purchase_time = datetime.now().strftime("%H:%M:%S")
    # email = session['email']


    #     return render_template("index.html", flights=data, changed_book=True, hide_header=True, roundtrip_date=True)
    # else:   
    #     data = unique_flight(airline_name, unique_airplane_num, flight_number, departure_date, departure_time)

    #     if (data):  
    #         base_price = price_modify(airline_name, unique_airplane_num, flight_number, departure_date, departure_time, base_price)

    #         query = 'INSERT into ticket Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    #         cursor.execute(query, (ticket_id, airline_name, unique_airplane_num, flight_number, departure_date, departure_time, card_type, card_number, name_on_card, expiration, base_price, email, purchase_date, purchase_time))
    #         conn.commit()
    #         cursor.close()

    #     return render_template('submitted.html')
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

