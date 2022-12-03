
insert into Airline values
	('Jetblue');

insert into Airport 
values
	('JFK', 'New York City','United States', 'Both'),
	('PVG', 'Shanghai', 'China', 'Both');
insert into Customers values 
	('test@nyu.edu', 'sonic', 'Test', 3, 'Sonic Drive', 'Chicago', 'IL', '123412341234', '123412341', '2025-10-21', 'United States', '2002-02-02'),
	('firstemail@nyu.edu', 'sonic2', 'First', 23, 'Email Drive', 'Emailland', 'KA', '686868686868', '767676767', '2025-10-20', 'United States', '2001-02-02'),
	('totallylegit@nyu.edu', 'password', 'Not Password', 26, 'Password Drive', 'Los Angeles', 'CA', '123432641434', '523422145', '2028-11-11', 'United States', '1999-06-02');
insert into airplane VALUES 
	('JetBlue', 1234123412, 123, 'HedgeInd', 10), 
	('JetBlue', 9999999999, 23, 'MauriceInd', 5),
	('JetBlue', 1111111111, 42, 'OliveGarden', 2) ;

insert into AirlineStaff values
	('Sonic', 'Jetblue', 'TheHedgehog', 'Olgilvie', 'Maurice',  '2005-06-23'),
    ('Genie', 'Jetblue', 'FriendLikeMe', 'Robin', 'Williams',  '1992-11-25'); 
		


insert into Flight values
        ('Jetblue', 1234123412, 1, '2022-10-31', '06:30:22', '2022-10-31', '20:13:32', 500, 'ontime', TRUE, 'JFK', 'PVG'),
        ('Jetblue', 1234123412, 1, '2022-10-31', '21:00:00', '2022-11-01', '11:17:18', 500, 'delayed', TRUE, 'PVG', 'JFK'),
        ('Jetblue', 9999999999, 2, '2022-11-07', '21:00:00', '2022-11-08', '11:32:27', 500, 'delayed', FALSE, 'PVG', 'JFK'),
        ('Jetblue', 1111111111, 3, '2022-11-10', '6:00:00', '2022-11-10', '20:44:29', 500, 'delayed', FALSE, 'JFK', 'PVG');
 

insert into Ticket values
    ('12345', 'Jetblue', 1234123412, 1, '2022-10-31', '06:30:22', 'credit', '4815931008084001', 'not password the 2nd', '2024-10-30', 500, 'totallylegit@nyu.edu',  '2022-10-01', '6:00:00'),
    ('45678', 'Jetblue', 1234123412, 1, '2022-10-31', '06:30:22', 'credit', '4815931008084001', 'not password the 2nd', '2024-10-30', 500, 'totallylegit@nyu.edu', '2022-10-01', '21:00:00'),
    ('23454', 'Jetblue', 1234123412, 1, '2022-10-31', '06:30:22', 'credit', '1234123412341234', 'Sonic the Hedgehog', '2025-1-1', 30, 'test@nyu.edu', '2022-10-29', '06:30:20');
