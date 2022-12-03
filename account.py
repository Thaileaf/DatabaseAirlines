from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
from helperFuncs import *
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



@app.route('/myaccount')
def myaccount():
	if "email" in session:
		return redirect('/Customers/customer')
	elif "username" in session:
		return redirect('/Staff/staff')



@app.route('/Staff/staff')
@role_required("Staff")
def staff():
    airports = get_airports();
    return render_template("Staff/staff.html", airports = airports);


@app.route('/Customers/customer')
@role_required("Customer")
def customer():
    return render_template("Customers/customer.html");


@app.route('/Staff/createflight', methods=['POST'])
@role_required("Staff")
def createflight():
    airport = request.form['airport'];
    # airport = request.form[]
