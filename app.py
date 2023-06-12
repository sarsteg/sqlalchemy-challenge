# Import the dependencies.
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
def index():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipitation: api/v1.0/precipitation<br/>"
        f"List of stations: api/v1.0/stations<br/>"
        f"Temperature observations: api/v1.0/tobs<br/>"
        f"Temperature stats from start date: api/v1.0/<start><br/>"
        f"Temperature stats from start to end date: api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    sel = [measurement.date,measurement.prcp]
    query_result = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in query_result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.rout("api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [station.station, station.name, station.latitude, station.longitude, station.elevation]
    query_result = session.query(*sel).all()
    session.close()

    stations = []
    for station, name, lat, lon, el in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
    session = Session(engine)
    lateststr = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route("/api/v1.0/<start>")


# Dynamic Routes

@app.route("/api/v1.0/<start>/<end>")

if __name__ == '__main__':
    app.run(debug=True)