# Import dependencies
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Create connection to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Surfs Up API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all dates and precipitation values"""
    # Create session (link) from Python to the DB
    # It's necessary to create the session every time that the page is called
    # to avoid thread errors
    session = Session(engine)
    
    # Query precipitation data  
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create dictionary from the data
    prcp = {}

    for result in results:
        prcp[result.date] = result.prcp

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Query precipitation data  
    results =  session.query(Station.station).all()

    # Convert list of tuples into normal list
    st = list(np.ravel(results))

    return jsonify(st)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all dates and temperature observations from a year from the last data point"""
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    # Find last data point date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d').date() - relativedelta(years=1)
    
    # Query precipitation data  
    results =  session.query(Measurement.date, Measurement.tobs).\
                       filter(Measurement.date >= year_ago).\
                       order_by(Measurement.date).\
                       all()

    # Convert list of tuples into normal list
    tob = list(np.ravel(results))

    return jsonify(tob)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a list of all dates and temperature observations from a start date"""
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Query precipitation data  
    results =  session.query(func.min(Measurement.tobs), 
                         func.max(Measurement.tobs), 
                         func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start_dt).\
                         all()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results))

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temp_stend(start, end):
    """Return a list of all dates and temperature observations from a start date to a end date"""
    # Create session (link) from Python to the DB
    session = Session(engine)
    
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d').date()

    end_dt = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Query precipitation data  
    results =  session.query(func.min(Measurement.tobs), 
                         func.max(Measurement.tobs), 
                         func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start_dt).\
                         filter(Measurement.date <= end_dt).\
                         all()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results))

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)