SELECT airline_name, unique_airplane_num, flight_number, departure_date, departure_time FROM flight WHERE departure_date > CAST( CURRENT_DATE() AS Date );

SELECT airline_name, unique_airplane_num, flight_number, departure_date, departure_time FROM flight WHERE status_flight = 'delayed';

SELECT DISTINCT name FROM ticket NATURAL JOIN customers; 

SELECT unique_airplane_num FROM airplane where airline_name = 'Jetblue';
