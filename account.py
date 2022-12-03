from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys

@app.route('/myaccount')
def myaccount():
	if "email" in session:
		return redirect('/Customers/customer')
	elif "username" in session:
		return redirect('/Staff/staff')

@app.route('/Staff/staff')
def staff():
    return render_template("Staff/staff.html");

@app.route('/Customers/customer')
def customer():
    return render_template("Customers/customer.html");



