"""
Resource: BrevetsResource
"""
from flask import Response, request, Flask
from flask_restful import Resource
import logging
from datetime import datetime

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

from database.models import Brevet


class BrevetsResource(Resource):
    def get(self):
        json_object = Brevet.objects().to_json()
        return Response(json_object, mimetype="application/json", status=200)

    def post(self):
        input_json = request.json
        
        app.logger.debug(input_json)
        input_json["begin_date"] = datetime.strptime(input_json["begin_date"], '%Y-%m-%dT%H:%M')
        
        for control in input_json['controls']:
            control['open_time'] = datetime.strptime(control['open_time'], '%Y-%m-%dT%H:%M')
            control['close_time'] = datetime.strptime(control['close_time'], '%Y-%m-%dT%H:%M')
        
        result = Brevet(**input_json).save()
        #app.logger.debug(result["begin_date"])
        return {'_id': str(result.id)}, 200
