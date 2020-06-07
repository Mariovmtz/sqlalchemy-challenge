import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#----------------------------------------------------------
# SETUP CODE COPIED AND PASTED FROM JUPYTER NOTEBOOK
#----------------------------------------------------------
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base = automap_base()
base.prepare(engine, reflect=True)

Measurement = base.classes.measurement
Station = base.classes.station

session = Session(engine)
#----------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------
def getListAllPrecipitation() -> list:
    return session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

def getListStations() -> list:
    return session.query(Measurement.station, func.count(Measurement.station).label('count')).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

def getListTobs(station: str, fromDate:str) -> list:
    return session.query(Measurement.date, Measurement.tobs).\
         filter(Measurement.date >= fromDate).\
         filter(Measurement.station == station).all()

def getMinMaxAvg(stdate: str, endDate: str) -> list:
    return session.query(func.min(Measurement.tobs).label('min'), func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')).\
        filter(Measurement.date >= stdate).\
        filter(Measurement.date <= endDate).all()
    
def getMostActiveStation() -> str:
    stations = getListStations()
    return stations[0][0]

def getLastDate() -> str:
    return session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).scalar()

# RETURNS EDATE - 365 DAYS, EDATE MUST BE SPECIFIED IN YYYY-MM-DD
def getOneYearfromDate(eDate: str) -> str:
    return str(dt.datetime.strptime(eDate, '%Y-%m-%d').date() - dt.timedelta(days=365))

#----------------------------------------------------------
# FLASK CODE
#----------------------------------------------------------
app = Flask(__name__)

# Main route to list all avaibale routes, main page.
@app.route("/")
def main():
    return (
        f"Welcome to Hawaii climate APP !!<br/>"
        f"List of available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YOUR START DATE HERE/<br/>"
        f"/api/v1.0/YOUR START DATE HERE/YOUR END DATE HERE/"
    )

# route /api/v1.0/precipitation"
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    result = getListAllPrecipitation()
    list_precip = []
    for precip in result:
        precip_dict = {}
        precip_dict["date"] = precip.date
        precip_dict["prcp"] = precip.prcp
        list_precip.append(precip_dict)
    #RETURNING THE JSON FROM THE DICTIONARY CREATED ABOVE
    return jsonify(list_precip)
#--------------------------------------------------------------
# route /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():

    result = getListStations()
    list_stations =[]
    for station in result:
        station_dict = {}
        station_dict["station"] = station.station
        station_dict["count"] = station.count
        list_stations.append(station_dict)
    #RETURNING THE JSON FROM THE DICTIONARY CREATED ABOVE
    return jsonify(list_stations)
#--------------------------------------------------------------
# route /api/v1.0/tobs"
@app.route("/api/v1.0/tobs")
def tobs():
    
    lastdate = getLastDate()
    mstation = getMostActiveStation()
    result = getListTobs(mstation, getOneYearfromDate(lastdate))
    last_tobs=[]
    for tob in result:
        tobs_dict = {}
        tobs_dict["station"] = mstation
        tobs_dict["date"] = tob.date
        tobs_dict["tob"] = tob.tobs
        last_tobs.append(tobs_dict)
    
    return jsonify(last_tobs)
#--------------------------------------------------------------
#  route /api/v1.0/<start_date>"
@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start(start_date, end_date='2099-12-31'):

    result = getMinMaxAvg(start_date, end_date)
    list_stats=[]
    for stat in result:
        dic_stats = {}
        dic_stats["D_START"] = start_date
        dic_stats["D_END"] = end_date
        dic_stats["TMIN"] = stat.min
        dic_stats["TAVG"] = stat.avg
        dic_stats["TMAX"] = stat.max
        list_stats.append(dic_stats)

    return jsonify(list_stats)
#--------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)