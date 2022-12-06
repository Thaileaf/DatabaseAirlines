#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import sys
from datetime import datetime, timedelta, date
from dateutil import rrule
import re
import random

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

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)