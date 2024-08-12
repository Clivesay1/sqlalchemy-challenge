# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy	

#Create connection to the sqlite file
engine = create_engine("sqlite:///hawaii.sqlite")

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

#Initialize the Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Create Flask Routes
@app.route("/")
def welcome():
	return (
		f"Welcome to the Hawaii climate api!<br/>"
		f"Available Routes:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/temp/start/end"
	)

#Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

	#Create Session
	session = Session(engine)

	# Calculate the date 1 year ago from the last data point in the database
	prev_year = dt.date(2016, 8, 23) - dt.timedelta(days=365)

	# Perform a query to retrieve the data and precipitation scores
	results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

	# Create a dictionary with the date as the key and the precipitation as the value
	precip = {date: prcp for date, prcp in results}
	return jsonify(precip)

	#close Session
	session.close()


#Create stations route
@app.route("/api/v1.0/stations")
def stations():

	#Create Session
	session = Session(engine)

	#Return a JSON list of stations from the dataset
	results = session.query(Station.station).all()

	#Unravel results into a 1D array and convert to a list
	stations = list(np.ravel(results))

	return jsonify(stations)

	#close Session
	session.close()

#Create temperature observations route
@app.route("/api/v1.0/tobs")
def temp_monthly():

	#Create Session
	session = Session(engine)

	#Calculate the date 1 year ago from the last data point
	prev_year = dt.date(2016, 8, 23) - dt.timedelta(days=365)

	#Query the primary station for all temperature observations from the last year
	results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all()

	#Create a list of temperatures from the results
	temps = list(np.ravel(results))

	return jsonify(temps)

	#close Session
	session.close()

#Create start route
@app.route("/api/v1.0/temp/<start>")

def stats(start=None, end=None):
	
	#Create Session
	session = Session(engine)

	#Select statement
	sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

	#If no end date is provided, calculate TMIN, TAVG, and TMAX for dates greater than and equal to the start date
	if not end:
		results = session.query(*sel).filter(Measurement.date >= start).all()
		temps = list(np.ravel(results))
		return jsonify(temps)

	#Calculate TMIN, TAVG, and TMAX with start and end dates
	results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
	temps = list(np.ravel(results))
	return jsonify(temps)

	#close Session
	session.close()

#Create start and end route
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
	
	#Create Session
	session = Session(engine)

	#Select statement
	sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

	#Calculate TMIN, TAVG, and TMAX with start and end dates
	results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
	temps = list(np.ravel(results))
	return jsonify(temps)

	#close Session
	session.close()

#Run the app
if __name__ == '__main__':
	app.run(debug=True)







