#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import sys
from datetime import datetime, timedelta, date
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
import staff
from helperFuncs import *

#Define a route to hello function
@app.route('/')
def root():
	cursor = conn.cursor()
	flights = getFutureFlights()
	airports = get_airports()
	cursor.close()
	
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



@app.route('/cancelTicket', methods=["GET", "POST"])
def cancelTicket():
	cursor = conn.cursor()
	email = "totallylegit@nyu.edu"
	ticket_id = int(float(request.form['ticket_id']))

	#check that the ticket_id is in your email so you can't delete someone elses ticket
	query = 'SELECT * from ticket where email = %s and ticket_id = %s'
	cursor.execute(query, (email, ticket_id))
	data = cursor.fetchone()
	print(ticket_id)

	if (data):
		query = 'DELETE from ticket where ticket.ticket_id = %s' # only works temporarily? a bit strange 
		cursor.execute(query, (ticket_id))
	
	cursor.close()
	return render_template('submitted.html')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)