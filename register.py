from __main__ import app, render_template, request, session, url_for, redirect, conn
import pymysql.cursors
import hashlib
import sys
#Define route for login
@app.route('/login')
def login(isCus = True):
	return render_template('LoginAuth/login.html', value = isCus)

#Define route for register
@app.route('/signup')
def signup():
	return render_template('LoginAuth/signup.html')

@app.route('/userSignUp')
def userSignUp():
	return render_template('LoginAuth/userSignUp.html')

@app.route('/staffSignUp')
def staffSignUp():
	query = "SELECT airline_name FROM Airline"
	cursor = conn.cursor() 
	cursor.execute(query)
	data = cursor.fetchall()
	print(data)
	ret = [{"name": d["airline_name"]} for d in data]
	return render_template('LoginAuth/staffSignUp.html', data = ret)

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	
	password = request.form['password']#.md5() # REMINDER ENCRYPTION
	hashed_password = hashlib.md5(password.encode())
	hashed_password = hashed_password.hexdigest()

	customer = True if "email" in request.form else False;
	print(hashed_password)

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	if customer:
		email = request.form['email']
		query = 'SELECT * FROM customers WHERE email = %s and password = %s'
		cursor.execute(query, (email, hashed_password))
		
	else:
		username = request.form['username']
		query = 'SELECT * FROM airlinestaff WHERE username = %s and password = %s'
		cursor.execute(query, (username, hashed_password))
	
	
	#stores the results in a variable
	
	data = cursor.fetchone()
	print(data)
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if (data):
		#creates a session for the the user
		#session is a built in
		if customer:
			session['email'] = email
		else:
			session['username'] = username;
		return redirect('/')
	else:
		#returns an error message to the html page
		if customer: 
			error = 'Invalid password or email'
			value = True 
		else: 
			error = 'Invalid password or username'
			value = False
		

		return render_template('LoginAuth/login.html', error=error, value = value )

#Authenticates the user register
@app.route('/userRegisterAuth', methods=['GET', 'POST'])
def registerUserAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	name = request.form['name']
	buildNum = int(request.form['buildnum'])
	street = request.form['street']

	city = request.form['city']
	state = request.form['state']
	phoneNum = request.form['pnum']
	passNum = request.form['passnum']
	passExp = request.form['passexp']

	passCon = request.form['passcon']
	bday = request.form['bday']

	hashed_password = hashlib.md5(password.encode())
	hashed_password = hashed_password.hexdigest()

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customers WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	passExp += "-01"
	if (data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('LoginAuth/userSignUp.html', error = error)
	else:
		print(passExp)
		print(password, hashed_password)
		ins = 'INSERT INTO Customers VALUES(%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s);'
		print((email, hashed_password, name, buildNum, street, city, state, phoneNum, passNum, passExp, passCon, bday))
		cursor.execute(ins, (email, hashed_password, name, 
		buildNum, street, city, 
		state, phoneNum, passNum, 
		passExp, passCon, bday))
		conn.commit()
		cursor.close()
		return login(True)

#Authenticates the Staff register
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def registerStaffAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	airline = request.form['airline']
	firstName = request.form['first name']
	lastName = request.form['last name']
	bday = request.form['bday']
	
	hashed_password = hashlib.md5(password.encode())


	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM airlinestaff WHERE username = %s'
	cursor.execute(query, (username))
	
	#stores the results in a variable
	userData = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	query = 'SELECT * FROM airline WHERE airline_name = %s'
	cursor.execute(query, (airline))
	airlineData = cursor.fetchone() 
	hashed_password = hashed_password.hexdigest()
	if (userData):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('LoginAuth/staffSignUp.html', error = error)
	if(not airlineData): 
		error = "Invalid Airline"
		return render_template('LoginAuth/staffSignUp.html', error = error)
	else:
		ins = 'INSERT INTO airlinestaff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (username, airline, hashed_password,firstName, lastName, bday))
		conn.commit()
		cursor.close()
		return login(False)


@app.route('/logout')
def logout():	
    if "email" in session:
        session.pop('email')
    elif "username" in session:
        session.pop('username')
        
    return redirect('/')