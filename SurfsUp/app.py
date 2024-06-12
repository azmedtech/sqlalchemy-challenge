# Import the dependencies.
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

# Save references to each table
# Assign Measurement and Station classes to variables with same names
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    last_12_months_data = session.query(Measurement.date, Measurement.prcp) \
    .filter(Measurement.date >= one_year_ago).all()

    # close the session
    session.close()

    # define a dictionary with date as key and prcp as value
    precip = {date:prcp for date, prcp in precipitation}

    return jsonify(precip)