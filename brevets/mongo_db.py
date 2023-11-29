# Mongo database functions

import os
from pymongo import MongoClient

# Set up MongoDB connection
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)

# use database brevets
db = client.brevets

# use conlection "controls" in the database
brevet_collection = db.controls

###
# Mongo database
###

def fetch_data():
    """
    Obtains the newest document in the "lists" collection in database "todo".

    Returns title (string) and items (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.
    form_data = brevet_collection.find().sort("_id", -1).limit(1)

    # form_data is a PyMongo cursor, which acts like a pointer.
    # We need to iterate through it, even if we know it has only one entry:
    for data in form_data:
        return data["brevet"], data["begin_date"], data["controls"]


def insert_data(brevet, begin_date, controls):
    """
    Inserts a new collection list into the database "brevet_collection", under the collection "lists".
    
    Inputs a title (string) and items (list of dictionaries)

    Returns the unique ID assigned to the document by mongo (primary key.)
    """
    output = brevet_collection.insert_one({
                     "brevet": brevet,
                     "begin_date": begin_date,
                     "controls": controls
                  })
    _id = output.inserted_id # this is how you obtain the primary key (_id) mongo assigns to your inserted document.
    return str(_id)