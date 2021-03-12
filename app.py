# 1. import Flask
from flask import Flask
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite/")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/enter requested start date in yyyy-mm-dd<br/>"
        f"/api/v1.0/enter requested start date in yyyy-mm-dd/enter requested end date in yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to obtain Precipitation information
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Add data obtained into a list
    prcp_list = []
    for date, prcp in prcp:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # query all stations
    stations = session.query(Station.id, Station.name).all()
    session.close()
    # Create a dictionary from the row data and append to a list
    station_info = []
    for id, name in stations:
        station_dict = {}
        station_dict["Station ID"] = id
        station_dict["Station Name"] = name
        station_info.append(station_dict)
    return jsonify(station_info)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session=Session(engine)

    # Query to obtain Temperatures information and most recent date
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    tobs_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
    session.close()
    
    # Add data obtained into a list
    tobs_info = []
    for date, tobs in tobs_year:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_info.append(tobs_dict)
    return jsonify(tobs_info)


#     Query most recent and oldest date in dataset    #

# Create our session (link) from Python to the DB
session = Session(engine)
start_dt = session.query(Measurement.date).order_by(Measurement.date.asc()).first()
start_dt = start_dt[0].replace("-", "")
end_dt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
end_dt = end_dt[0].replace("-", "")
session.close()

@app.route("/api/v1.0/<start>")
def search_date (start):
    session = Session(engine)
# #     # Query all stations and precips
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()  
    session.close()
    start_date_data = []
    for min, avg, max in results:
        start_date_data_dict = {}
        start_date_data_dict["min_temp"] = min
        start_date_data_dict["avg_temp"] = avg
        start_date_data_dict["max_temp"] = max
        start_date_data.append(start_date_data_dict) 
    return jsonify(start_date_data)

@app.route("/api/v1.0/<start>/<end>")
def two_dates (start,end):
    session = Session(engine)
# #     # Query all stations and precips
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()  
    session.close()
    start_end_date_data = []
    for min, avg, max in results:
        start__end_date_dict = {}
        start__end_date_dict["min_temp"] = min
        start__end_date_dict["avg_temp"] = avg
        start__end_date_dict["max_temp"] = max
        start__end_date_data.append(start_end_date_dict) 
    return jsonify(start_end_date_data)

if __name__ == '__main__':
    app.run(debug=True)
