# import the dependencies
import datetime as dt 
import numpy as np 
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func 
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# create engine using sqlite database file in Resources folder
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
# declare base variable using automap_base
Base = automap_base()

# reflect the tables
# use prepare function to create ORM classes (aligns incompatible types)
# ORM stands for Object-Relational Mapping. It is a programming technique used to convert data between incompatible type systems in object-oriented programming languages. Essentially, ORM allows you to interact with a relational database using an object-oriented paradigm. Here’s a detailed explanation:
Base.prepare(autoload_with=engine)

# save references to each table
# assign Measurement and Station classes to variables with same names
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# create an app, use pass__name__, and intitialize 
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# define precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return the precipitation data for the last year"""

    # calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # perform a query to retrieve the date and precipitation scores
    last_12_months_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).all()

    # close the session
    session.close()

    # define a dictionary with date as key and prcp as value and return as JSON
    precip = {date:prcp for date, prcp in precipitation}

    return jsonify(precip)

# define stations route
@app.route('/api/v1.0/stations')
def active_stations():
    """Return the list of stations from the dataset"""

    # perform a query to retrieve the active stations 
    active_stations_query = session.query(Station.station).all()
    
    # close the session
    session.close()

    # create and return a JSON list of all the stations in the dataset
    station_list = []
    for station in active_stations_query:
        station_list.append({'station': station})

    return jsonify(station_list)

# define dates and temperatures of most active stations route
@app.route('/api/v1.0/tobs')
def date_temp():
    """Returns the date and temperature observations from the most active stations over the previous year"""

    # calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # perform a query to retrieve the date and precipitation observations over the previous year
    active_stations = session.query(Station.station, func.count(Measurement.station)).\
        filter(Station.station == Measurement.station).\
        group_by(Station.station).\
        order_by(func.count(Measurement.station).desc()).all()

    # define the most active station
    most_active_station = active_stations[0,0]

    # perform a query for the previous year data for the most active station only
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >=one_year_ago).all()

    # close the session
    session.close()

    # create and return a JSON list of the temperature observations over the previous year
    tobs_list = [{date: tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# define the route for the specified start date
@app.route('/api/v1.0/<start>')
def temp_start(start):
    """Returns the minimum, maximum, and average temperature observations from a given start date through the end of the dataset"""

    # define the start date
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    
    # perform a query to pull the data for the approrpaite date range
    temp_data = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))./
        filter(Measurement.date >= start_date).all()
    
    # close the session
    session.close()

    # create and return a JSON list of the temperature observations 
    temp_data_dict = {"Tmin": temp_data[0][0], "Tmax": temp_data[0][1], "Tavg": temp_data[0][2]}
    
    return jsonify(temp_data_dict)

# define the route for the specified start and end date
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    """Returns the minimum, maximum, and average temperature observations between given start and end dates"""

    # define the start and end dates
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
    # perform a query to pull the data for the approrpaite date range
    temp_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))./
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    # close the session
    session.close()

    # create and return a JSON list of the temperature observations 
    temp_range_dict = {"Tmin": temp_range[0][0], "Tmax": temp_range[0][1], "Tavg": temp_range[0][2]}
    
    return jsonify(temp_range_dict)

if __name__ == '__main__':
    app.run(debug=True)