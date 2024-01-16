# Import the dependencies.

from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import os
from pathlib import Path

current_directory = Path.cwd()
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#################################################
# Database Setup
#################################################
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Base.classes.keys()
Measure = Base.classes.measurement
session = Session(engine)
print(Measure)
# Create a Flask application
app = Flask(__name__)

# Define what to do when the user hits the homepage
@app.route("/")
def homepage():
    return """ <h1> Welcome to Honolulu, Hawaii Climate API! </h1>
    <h3> The available routes are: </h3>
    <ul>
    <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: <strong>/api/v1.0/precipitation</strong> </li>
    <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li>
    <li><a href = "/api/v1.0/tobs"> TOBS </a>: <strong>/api/v1.0/tobs</strong></li>
    <li>To retrieve the minimum, average, and maximum temperatures for a specific start date, use <strong>/api/v1.0/&ltstart&gt</strong> (replace start date in yyyy-mm-dd format)</li>
    <li>To retrieve the minimum, average, and maximum temperatures for a specific start-end range, use <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (replace start and end date in yyyy-mm-dd format)</li>
    </ul>
    """

# Define what to do when the user hits the precipitation URL
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    twelve_mo_ago = dt.date(2017,8,23) - dt.timedelta(days=365)


    # Query precipitation data from last 12 months from the most recent date from Measurement table
    prcp_data = session.query(Measure.date, Measure.prcp).\
    filter(Measure.date >= twelve_mo_ago()).all()
    
    # Close the session                   
    session.close()

    # Create a dictionary from the row data and append to a list of prcp_list
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return a list of jsonified precipitation data for the previous 12 months 
    return jsonify(prcp_list)

# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def stations():
    # Create the session
    session = Session(engine)

    # Query station data from the Station dataset
    station_dataset = session.query(Station.station).all()

    # Close the session                   
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_dataset))

    # Return a list of jsonified station data
    return jsonify(station_list)

# Define what to do when the user hits the URL
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    # Query tobs data from last 12 months from the most recent date from Measurement table
    tobs_data = session.query(Measure.date, Measure.tobs).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date >= date_prev_year()).all()

    # Close the session                   
    session.close()

    Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)

# Define what to do when the user hits the URL with a specific start date or start-end range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create the session
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    sel=[func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    
    # Check if there is an end date then do the task accordingly
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*sel).\
                            filter(Measure.date >= start).all()
        # Convert list of tuples into normal list
        start_list = list(np.ravel(start_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start_list)
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*sel).\
                            filter(Measure.date >= start).\
                            filter(Measure.date <= end).all()
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

    # Close the session                   
    session.close()
    
# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)