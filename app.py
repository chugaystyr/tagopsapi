# save this as app.py
from flask import Flask, request, jsonify, abort
from functools import wraps
from db import DB
import json

app = Flask(__name__)

# create database object
db = DB()

def authorize(request):
    if not 'TagopsSecret' in request.headers or not 'TagopsBucket' in request.headers :
        abort(401)

    tagopsSecret = request.headers.get("TagopsSecret")
    tagopsBucket = request.headers.get("TagopsBucket")

    abort(401) if not tagopsBucket or int(tagopsBucket) != 123 else ''
    abort(401) if not tagopsSecret or int(tagopsSecret) != 123 else ''
    return  tagopsBucket, tagopsSecret


@app.route("/tag", methods=["POST"])
def create_tag():
    tagopsBucket, tagopsSecret = authorize(request)
    res_json = request.data.decode('utf8').replace("'", '"')
    data = json.loads(res_json)
    if db.inset(int(tagopsSecret), int(tagopsBucket), data):
        return jsonify({'message':'Tag created.'}), 201
    else:
        return jsonify({'message':'Tag not created.'}), 500


@app.route("/tag/<tag_id>", methods=["GET"])
def tag_details(tag_id):
    tagopsBucket, tagopsSecret = authorize(request)
    res = db.get_tag(tag_id)
    response = {}
    if res:
        return jsonify(genrate_dict(res)), 200
    else:
        return jsonify({'messsage':"No data found"}), 200



@app.route("/user/tags", methods=["GET"])
def tag_list():
    tagopsBucket, tagopsSecret = authorize(request)
    rows = db.get_tag_list()
    response_list = []
    for row in rows:
        response_list.append(genrate_dict(row))
        return jsonify(response_list), 200
    else:
        return jsonify({'messsage':"No data found"}), 200


def genrate_dict(row):
    _dict = {}
    _dict.update({'id':row[0]}) if row[0] else ''
    _dict.update({'created':row[1].strftime("%Y-%m-%d")}) if row[1] else ''
    _dict.update({'jval':row[2]}) if row[2] else ''
    _dict.update({'val':row[3]}) if row[3] else ''
    _dict.update({'usersecret':row[4]}) if row[4] else ''
    _dict.update({'userbucket':row[5]}) if row[5] else ''
    return _dict





app.run(host="0.0.0.0", port=5000)
