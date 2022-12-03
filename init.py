#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

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



#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('LoginAuth/login.html')

#Define route for register
@app.route('/signup')
def signup():
	return render_template('LoginAuth/signup.html')

@app.route('/userSignUp')
def userSignUp():
	return render_template('LoginAuth/userSignUp.html')

@app.route('/staffSignUp')
def staffSignUp():
	return render_template('LoginAuth/staffSignUp.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']#.md5()
	hashed_password = hashlib.md5(password.encode())

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customers WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if (data):
		#creates a session for the the user
		#session is a built in
		session['email'] = email
		return redirect('/')
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('LoginAuth/login.html', error=error)

#Authenticates the user register
@app.route('/userRegisterAuth', methods=['GET', 'POST'])
def registerUserAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	# hashed_password = hashlib.md5(password.encode())

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customers WHERE email = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if (data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('LoginAuth/userSignUp.html', error = error)
	else:
		return render_template('index.html')
		ins = 'INSERT INTO customers VALUES(%s, %s)'
		cursor.execute(ins, (username, hashed_password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

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
	
	# hashed_password = hashlib.md5(password.encode())

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
	if (userData):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('LoginAuth/staffSignUp.html', error = error)
	if(not airlineData): 
		error = "Invalid Airline"
		return render_template('LoginAuth/staffSignUp.html', error = error)
	else:
		return render_template('index.html')
		ins = 'INSERT INTO customers VALUES(%s, %s)'
		cursor.execute(ins, (username, hashed_password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    # for each in data1:
        # print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor()
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():

	session.pop('username')
	return redirect('/')
		
@app.route('/staff')
def editPage():
	return render_template('Staff/staff.html')

@app.route('/reports')
def charts():
	return render_template('Staff/Reports/chart.html')

@app.route('/viewinfo')
def customer():
	return render_template('Customers/customer.html')




@app.route('/flightsearch')
def flightsearch():
	
	query = "SELECT * from flight where depart_from = %s, arrive_at = %s, departure_date=%s"
	return 

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)

