from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
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
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    year_ago=dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_score=session.query(Measurement.date,func.max(Measurement.prcp)).filter(func.strftime('%Y-%m-%d',Measurement.date) > year_ago).group_by(Measurement.date).all()
   
    session.close()

    all_precip = []
    for date, prcp in precip_score:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        all_precip.append(date_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_all = session.query(Station.name).all()
        # Convert list into normal list
    station_list = list(np.ravel(stations_all))
        # Return JSON 
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_active=[Measurement.station, 
             func.min(Measurement.tobs), 
             func.max(Measurement.tobs), 
             func.avg(Measurement.tobs)]

    most_active_station=(session.query(*most_active)
                       .filter(Measurement.station=='USC00519281')
                       .all())

    most_active_list = list(np.ravel(most_active_station))

    return jsonify(most_active_list)


if __name__ == '__main__':
    app.run(debug=True)

