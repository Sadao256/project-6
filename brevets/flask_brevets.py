"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os
import logging
import requests 

import arrow
import flask

from flask import request
import acp_times  

# Set up Flask app
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)

##################################################
################### API Callers ################## 
##################################################

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############


def get_times():
    """
    Obtains the newest document in the "lists" collection in database
    by calling the RESTful API.

    Returns title (string) and items (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.

    lists = requests.get(f"{API_URL}brevets").json()

    # lists should be a list of dictionaries.
    # we just need the last one:
    brevet = lists[-1]
    #app.logger.debug("got controls", brevet["controls"])
    return brevet["distance"], brevet["begin_date"], brevet["controls"]
    


def insert_times(distance, begin_date, controls):
    
    """ 
    
    Inserts a new brevet into the database by calling the API.

    """

    response = requests.post(f"{API_URL}brevets", json={"distance": distance, "begin_date": begin_date, "controls": controls})
    print(response.text)  # Print the raw server response
    _id = response.json()   

    # Return the ID 
    return _id


@app.route('/insert', methods=['POST'])
def insert():
    try:
        # Parse the JSON data from the request
        input_json = request.json
        #app.logger.debug(input_json)

        # Extract data from the JSON
        distance = input_json["distance"]
        #app.logger.debug(distance)
        begin_date = input_json["begin_date"]
        app.logger.debug("controls = %s", input_json["controls"])
        controls = input_json["controls"]


        # Insert data into the database
        app.logger.debug("insert times = %s", insert_times(distance, begin_date, controls))
        brevet_id = insert_times(distance, begin_date, controls)

        # Respond with a JSON message indicating success
        return flask.jsonify(result={},
                             message="Inserted!",
                             status=1,
                             mongo_id=brevet_id)
    except Exception as e:
        app.logger.debug("Oh no! Server error! Exception: %s", str(e))

        # Respond with a JSON message indicating failure
        return flask.jsonify(result={},
                             message="Oh no! Server error!",
                             status=0,
                             mongo_id='None')


@app.route("/fetch")
def fetch():
    """  
    
    fetch : fetches the brevet distance, control distance(s), open times, and close times from the database.

    Accepts GET requests ONLY!

    JSON interface: gets JSON, responds with JSON"""
 
    try:
        # Get the latest data from the database
        distance, begin_date, controls = get_times()  
        app.logger.debug("fetched!")
        #app.logger.debug("fetched controls", controls)
        # Respond with a JSON message indicating success
        return flask.jsonify(
                result={"distance": distance, "begin_date": begin_date, "controls": controls}, 
                status=1,
                message="Successfully fetched all data!")
    except Exception as e:
        app.logger.debug("Exception occurred: %s", str(e))

        # Respond with a JSON message indicating failure
        return flask.jsonify(
                result={}, 
                status=0,
                message="Something went wrong, couldn't fetch any times/distances!")

    
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from kilometers, using rules
    described at https://rusa.org/octime_alg.html.
    Expects three URL-encoded arguments.
    """
    app.logger.debug("Got a JSON request")
    
    # Get the Km from the Ajax request
    km = request.args.get('km', 999, type=float)
    
    # Get the start time from the Ajax request
    start_time_str = request.args.get('start_time')

    # Get the Brevet Distance from the Ajax request
    brevet_dist = request.args.get('distance', 200, type=int)
    
    # Convert the start_time string to an arrow object
    start_time = arrow.get(start_time_str)

   # Calculate the open time with the arguments km, brevet_dist, start_time
    open_time = acp_times.open_time(km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm:ss')

    # Calculate the close time with the arguments km, brevet_dist, start_time
    close_time = acp_times.close_time(km, brevet_dist, start_time).format('YYYY-MM-DDTHH:mm:ss')

    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)
    
#############

if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")