from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *


# Decorator
# Used to ensure only customers can access page
# Put under routes
def Customer(func):
    def check():
        if "email" in session:
            return func();
        else:
            return redirect("/login");
    return check;

# Decorator
# Used to ensure only Staff can access page
# Put under routes
def Staff(func):
    def check():
        if "username" in session:
            return func();
        else:
            return redirect("/login");
    return check;


@app.route('/myaccount')
def myaccount():
	if "email" in session:
		return redirect('/Customers/customer')
	elif "username" in session:
		return redirect('/Staff/staff')


@app.route('/Staff/staff')
@Staff
def staff():
    airports = get_airports();
    return render_template("Staff/staff.html", airports = airports);

@app.route('/Customers/customer')
def customer():
    return render_template("Customers/customer.html");


@app.route('/Staff/createflight', methods=['POST'])
def createflight():
    airport = request.form['airport'];
    # airport = request.form[]
