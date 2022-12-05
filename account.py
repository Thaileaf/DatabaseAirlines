from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *
from functools import wraps
from datetime import datetime



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


@app.route('/Staff/createflight', methods=['POST'])
@role_required("Staff")
def createflight():
    airport = request.form['airport'];
    # airport = request.form[]

@app.route('/Staff/frequentcustomers')
@role_required("Staff")
def frequentCustomer():
    query = """SELECT email as customer, count(email) as flights 
            FROM (
                SELECT *
                FROM ticket
                WHERE departure_date >= cast(DATE_ADD(CURDATE(), INTERVAL -1 YEAR) AS DATE)
                ) as TABLE1
            WHERE airline_name = %s
            GROUP BY email 
            ORDER BY count(email) DESC;"""

    queryAirline = "SELECT airline_name FROM airlinestaff WHERE username = %s;"

    cursor = conn.cursuor()