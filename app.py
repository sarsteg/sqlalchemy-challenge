# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Static Routes

@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as JSON."""
    session = Session(engine)
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (pd.to_datetime(last_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset as JSON."""
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations of the most-active station for the previous year as JSON."""
    session = Session(engine)
    last_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (pd.to_datetime(last_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(tobs_list)

# Dynamic Routes

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return the temperature statistics (TMIN, TAVG, TMAX) for a specified start or start-end range as JSON."""
    session = Session(engine)
    
    if end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
    session.close()
    
    if results:
        temperature_stats = {
            "TMIN": results[0][0],
            "TAVG": results[0][1],
            "TMAX": results[0][2]
        }
        return jsonify(temperature_stats)
    else:
        return jsonify({"error": "Invalid date range"}), 404


if __name__ == '__main__':
    app.run(debug=True)