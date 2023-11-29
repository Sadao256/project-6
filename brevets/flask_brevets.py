"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""
import logging

import os
import requests
import flask
from flask import request
import arrow  
import acp_times  

# Set up Flask app
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404

##################################################
################### API Callers ################## 
##################################################

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"


def get_brevet():
    """
    Obtains the newest document in the "brevets" collection in database
    by calling the RESTful API.
    Returns brevet_dist (string), datetime (datetime),
    and controls (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.
    brevets = requests.get(f"{API_URL}/brevets").json()

    # lists should be a list of dictionaries.
    # we just need the last one:
    brevet = brevets[-1]
    return brevet["length"], brevet["start_time"], brevet["checkpoints"]

def insert_brevet(brevet_dist, datetime, controls):
    """
    Inserts a new brevet into the database by calling the API.
    """

    _id = requests.post(f"{API_URL}/brevets", json={"length": brevet_dist, "start_time": datetime, "checkpoints": controls}).json()
    print(response.text)  # Print the raw server response
    _id = response.json()   
    return _id

##################################################
################## Flask routes ################## 
##################################################


@app.route("/insert", methods=["POST"])
def insert():
    try: 
        # Read the entire request body as a JSON
        # This will fail if the request body is NOT a JSON.
        input_json = request.json
        # if successful, input_json is automatically parsed into a python dictionary!
        
        # Because input_json is a dictionary, we can do this:
        brevet = input_json["brevet"] 
        begin_date = input_json["begin_date"] 
        controls = input_json["controls"]

        brevet_id = insert_brevet(brevet, begin_date, controls)

        return flask.jsonify(result={},
            message="Inserted!", 
            status=1, # This is defined by you. You just read this value in your javascript.
            mongo_id=brevet_id)
    
    except Exception as e:
        app.logger.error(f"Error fetching brevet: {str(e)}")
        return flask.jsonify(
            result={}, 
            status=0,
            message=f"Something went wrong: {str(e)}"
    )


@app.route("/fetch")
def fetch():
        """
        /fetch : fetches the newest to-do list from the database.

        Accepts GET requests ONLY!

        JSON interface: gets JSON, responds with JSON
        """
        try:
            brevet, begin_date, controls = get_brevet()
            return flask.jsonify(
                result={"brevet": brevet, "begin_date": begin_date, "controls":controls}, 
                status=1,
                message="Successfully fetched a brevet list!")
        except:
            return flask.jsonify(
                result={}, 
                status=0,
                message="Something went wrong, couldn't fetch any lists!")


@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from kilometers, using rules
    described at https://rusa.org/octime_alg.html.
    Expects three URL-encoded arguments: km, start_time, and brevet_dist.
    """
    app.logger.debug("Got a JSON request")
    
    # Get the Km from the Ajax request
    km = request.args.get('km', 999, type=float)
    
    # Get the start time from the Ajax request
    start_time_str = request.args.get('start_time')

    # Get the Brevet Distance from the Ajax request
    brevet_dist = request.args.get('brevet_dist', 200, type=int)
    
    # Convert the start_time string to an arrow object
    start_time = arrow.get(start_time_str)

    # calculate the open time with the arguements km, brevet_dist, start_time using open_time function in the file acp_times
    open_time = acp_times.open_time(km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm')

    # calculate the close time with the arguements km, brevet_dist, start_time using close_time function in the file acp_times
    close_time = acp_times.close_time(km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm')

    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)



#############

if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")

