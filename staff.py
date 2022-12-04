from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
import datetime
from helperFuncs import *

@app.route('/FlightEditor')
@role_required("Staff")
def flightEditor():
	ap = get_airports()
	planes = getAirplanes()
	staffAirline = session["staffAirline"]
	return render_template('Staff/FlightEditor.html', airports = ap, planes = planes, airline = staffAirline)


@app.route('/FlightEditor/addFlight', methods=['GET', 'POST'])
@role_required("Staff")
def addFlight(): 
	ap = get_airports()
	planes = getAirplanes()
	staffAirline = session["staffAirline"]
	arrAirport = request.form['arrAir']
	depAirport = request.form['depAir']
	flightnum = request.form['flightnum']
	depTime = request.form["dptime"]
	depDate = request.form['dpdate']
	arrTime = request.form["artime"]
	arrDate = request.form['ardate']
	depDT = datetime.datetime.strptime(depDate +" "+depTime, '%Y-%m-%d %H:%M')
	arrDT = datetime.datetime.strptime(arrDate + " "+arrTime, '%Y-%m-%d %H:%M')
	roundTrip = False
	if(depAirport == arrAirport): 
		addFlightError = "Invalid Flight Departure and Arrival Airport are the Same"
		return render_template('Staff/FlightEditor.html', airports = ap, planes = planes, airline = staffAirline, addFlightError = addFlightError, addingFlight = True)

	if(findFlight(staffAirline, flightnum)): 
		addFlightError = "Flight Number Already Exists"
		return render_template('Staff/FlightEditor.html', airports = ap, planes = planes, airline = staffAirline, addFlightError = addFlightError, addingFlight = True)

	if(arrDT < depDT):
		addFlightError = "Invalid Date and Time, Arrival is Before Departure"
		return render_template('Staff/FlightEditor.html', airports = ap, planes = planes, airline = staffAirline, addFlightError = addFlightError, addingFlight = True)
		
	
	values = ( session["staffAirline"], request.form['airplane'], flightnum, request.form['dpdate'], 
	request.form['dptime'], request.form['ardate'], request.form['artime'], request.form['baseprice'], 
	request.form['status'], roundTrip, depAirport, arrAirport
	)
	query = "INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	cursor = conn.cursor() 
	cursor.execute(query, values)
	conn.commit()
	return render_template('Staff/FlightEditor.html', airports = ap, planes = planes, airline = staffAirline, addFlightError = "Flight Successfully Added", addingFlight = True)