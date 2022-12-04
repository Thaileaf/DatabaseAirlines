create table Airline(
	airline_name 			varchar(20) NOT NULL,
	PRIMARY KEY(airline_name)
);
create table Airplane(
	airline_name			VARCHAR(20) NOT NULL,	
	unique_airplane_num		DOUBLE(10,0) UNSIGNED NOT NULL,
	num_of_seats 		DOUBLE(4,0) UNSIGNED NOT NULL,
	manufact_comp		VARCHAR(20) NOT NULL,
	age_of_airplane		DOUBLE(10, 0) UNSIGNED NOT NULL,
	PRIMARY KEY(airline_name, unique_airplane_num),
	FOREIGN KEY(airline_name) references Airline(airline_name)
	
);

create table Airport(
	name				VARCHAR(20) NOT NULL, 
	city				VARCHAR(20) NOT NULL,
	country 			VARCHAR(20) NOT NULL, 
	type 				VARCHAR(15) CHECK (type in ('domestic', 'international', 'both')),
	PRIMARY KEY(name)
);

create table Flight(
	airline_name			VARCHAR(20) NOT NULL,
	unique_airplane_num		DOUBLE(10, 0) UNSIGNED NOT NULL,
	flight_number			DOUBLE(10, 0) UNSIGNED NOT NULL,
	departure_date		DATE NOT NULL,
	departure_time		TIME(3) NOT NULL,
	arrival_date			DATE NOT NULL,
	arrival_time			TIME(3) NOT NULL,
	base_price			DOUBLE(10, 0) UNSIGNED NOT NULL, 
	status_flight			VARCHAR(10) NOT NULL CHECK (status_flight in ('delayed', 'ontime', 'canceled')),
	roundtrip			BOOLEAN,
	depart_from			VARCHAR(20),
	arrive_at			VARCHAR(20),
	PRIMARY KEY (airline_name, unique_airplane_num, flight_number, departure_date, departure_time),
   	FOREIGN KEY (airline_name, unique_airplane_num) REFERENCES Airplane(airline_name, unique_airplane_num),
	FOREIGN KEY (depart_from) REFERENCES Airport(name),
	FOREIGN KEY (arrive_at) REFERENCES Airport(name)
);


create table Ticket(
	ticket_id 			DOUBLE(10, 0) NOT NULL, 
airline_name			VARCHAR(20) NOT NULL,
	unique_airplane_num		DOUBLE(10, 0) UNSIGNED NOT NULL,
	flight_number 			DOUBLE(10, 0) UNSIGNED NOT NULL, 
	departure_date 		DATE NOT NULL,
	departure_time 		TIME (3) NOT NULL,
	card_type			VARCHAR(6) CHECK (card_type in ('credit', 'debit')),
	card_number			DOUBLE(16, 0) NOT NULL,
	name_on_card		VARCHAR(30),
	expiration_date		DATE,
	sold_price			SMALLINT(5) UNSIGNED,
	email				VARCHAR(20) NOT NULL,
	purchase_date		DATE NOT NULL,
	purchase_time		TIME(3) NOT NULL,
PRIMARY KEY (ticket_id),
FOREIGN KEY (airline_name, unique_airplane_num, flight_number, departure_date, departure_time) REFERENCES Flight(airline_name, unique_airplane_num, flight_number, departure_date, departure_time)
);

create table Ratings(
	email				VARCHAR(20) NOT NULL,
	airline_name			VARCHAR(20) NOT NULL,
unique_airplane_num		DOUBLE(10, 0) UNSIGNED NOT NULL,
	flight_number 			DOUBLE(10, 0) UNSIGNED NOT NULL, 
	departure_date		DATE  NOT NULL,
	departure_time		TIME(3) NOT NULL,
	rating				TINYINT(1) NOT NULL CHECK (rating  > 0 and rating < 6),
	comment_ratings		VARCHAR(600),
    
	PRIMARY KEY(email, airline_name, unique_airplane_num, flight_number, departure_date, departure_time),
	FOREIGN KEY(airline_name, unique_airplane_num, flight_number, departure_date, departure_time) references Flight(airline_name, unique_airplane_num, flight_number, departure_date, departure_time)
);

create table Customers(
	email 				VARCHAR(20) NOT NULL,
	password 			VARCHAR(32) NOT NULL, 
	name 				VARCHAR(20) NOT NULL, 
	building_number 		DOUBLE(10, 0) UNSIGNED NOT NULL,
	street 				VARCHAR(30) NOT NULL,
	city 				VARCHAR(20) NOT NULL,
	state 				VARCHAR(20) NOT NULL,
	phone_number		 VARCHAR(20),
	passport_number 	    VARCHAR(20) NOT NULL,
	passport_expiration 		DATE NOT NULL,
	passport_country 		VARCHAR(20) NOT NULL, 
	date_of_birth 			DATE NOT NULL
);

create table AirlineStaff(
	username 			VARCHAR(20) NOT NULL,
	airline_name			VARCHAR(20) NOT NULL, 
	password			VARCHAR(32) NOT NULL, 
	first_name			VARCHAR(20),
	last_name			VARCHAR(20), 
	date_of_birth			DATE, 
	PRIMARY KEY (username, airline_name),
	FOREIGN KEY (airline_name) references Airline(airline_name)
);
create table PhoneNumber(
	username			VARCHAR(20) NOT NULL,
	airline_name			VARCHAR(20) NOT NULL,
	phone_number		CHAR(12),
PRIMARY KEY (username, airline_name, phone_number),
FOREIGN KEY (username, airline_name) references AirlineStaff(username, airline_name)
);

create table EmailAddress(
	username			VARCHAR(20) NOT NULL,
	airline_name			VARCHAR(20) NOT NULL,
	email_address	 		VARCHAR(20) NOT NULL,
	PRIMARY KEY (username, airline_name, email_address),
	FOREIGN KEY (username, airline_name) references AirlineStaff(username, airline_name)

);
