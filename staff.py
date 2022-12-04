from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *

@app.route('/FlightEditor')
@role_required("Staff")
def flightEditor():
	ap = get_airports()
	planes = getAirplanes()
	return render_template('Staff/FlightEditor.html', airports = ap, planes = planes)


@app.route('/FlightEditor/addFlight', methods=['GET', 'POST'])
@role_required("Staff")
def addFlight(): 
    pass