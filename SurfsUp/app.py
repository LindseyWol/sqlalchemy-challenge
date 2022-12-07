import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Station List: /api/v1.0/stations<br/>"
        f"Temps for most active station last year of data: /api/v1.0/tobs<br/>"
        f"Temp stats from a start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temp stats for a range of dates (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.   
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Return precipitation from 8/23/2016-8/23/2017"""
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    
    session.close()

    last_year_prcp = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["precipitation"] = prcp
        last_year_prcp.append(measurement_dict)

    return jsonify(last_year_prcp)

#Return list of stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    stations = session.query(Station.station).all()

    session.close()

    station_ls = list(np.ravel(stations))
    return jsonify(station_ls)

#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
   #find last date entry for station USC00519281
    mas_lastdate = session.query(Measurement.date)\
    .filter(Measurement.station == 'USC00519281')\
    .order_by(Measurement.date.desc()).first()

    #calculate date one year prior to last date of 8/18/2017
    mas_yearago = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    #filter for dates between 8/18/2016 and 8/18/2017 for station USC00519281
    mas_yeardata = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date >= mas_yearago)\
    .filter(Measurement.station == 'USC00519281').all()

    mas_all = []
    for date, tobs in mas_yeardata:
        mas_dict = {}
        mas_dict["Date"] = date
        mas_dict["Tobs"] = tobs
        mas_all.append(mas_dict)

    return jsonify(mas_all)

#For a specified start date calculate TMIN, TAVG, and TMAX 
@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_stats = []
    for min,avg,max in queryresult:
        start_dict = {}
        start_dict["Min"] = min
        start_dict["Average"] = avg
        start_dict["Max"] = max
        start_stats.append(start_dict)

    return jsonify(start_stats)

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    range_all = []
    for min,avg,max in queryresult:
        range_dict = {}
        range_dict["Min"] = min
        range_dict["Average"] = avg
        range_dict["Max"] = max
        range_all.append(range_dict)

    return jsonify(range_all)


if __name__ == '__main__':
    app.run(debug=True)

