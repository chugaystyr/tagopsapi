# save this as app.py
from flask import Flask, request, jsonify, abort
from functools import wraps
from db import DB
import json
import uuid
import hashlib
from config import *


app = Flask(__name__)

# create database object
db = DB()


class Tags:

    def __init__(self):
        self.tagopsSecret = None
        self.tagopsBucket = None

tags = Tags()

def authorize(request):

    if 'TagopsSecret' in request.headers and 'TagopsBucket' in request.headers :
            validate(request)
            tagopsSecret = request.headers.get("TagopsSecret")
            tagopsBucket = request.headers.get("TagopsBucket")

    elif tags.tagopsSecret and tags.tagopsBucket:
            tagopsSecret = tags.tagopsSecret
            tagopsBucket = tags.tagopsBucket
    else:
        abort(401)

    db.buked_id = tagopsBucket
    return  tagopsBucket, tagopsSecret


def validate(request):
    tagopsSecret = request.headers.get("TagopsSecret")
    tagopsBucket = request.headers.get("TagopsBucket")
    user_id = 0
    url = request.url.split('/')
    if (len(url) == 5) and (url[::-1][1] == 'users'):
        user_id = int(url[::-1][0])
    res = db.validate_tokens(tagopsSecret, tagopsBucket, user_id)
    if(res):
        tags.tagopsSecret = res[3]
        tags.tagopsBucket = res[4]
        return True
    else:
        abort(401)


@app.route("/tag", methods=["POST"])
def create_tag():
    tagopsBucket, tagopsSecret = authorize(request)
    res_json = request.data.decode('utf8').replace("'", '"')
    data = json.loads(res_json)
    tag_id = db.inset(tagopsSecret, tagopsBucket, data)
    if tag_id:
        res = db.get_tag(tag_id[0])
        context = genrate_dict(TAG_FIELDS, res)
        context['message'] = "Tag created!"
        return jsonify(context), 201
    else:
        return jsonify({'message':'Tag not created.'}), 500


@app.route("/tag/<tag_id>", methods=["GET"])
def tag_details(tag_id):
    tagopsBucket, tagopsSecret = authorize(request)
    res = db.get_tag(tag_id)
    response = {}
    if res:
        return jsonify(genrate_dict(TAG_FIELDS, res)), 200
    else:
        return jsonify({'messsage':"No data found"}), 200



@app.route("/user/tags", methods=["GET"])
def tag_list():
    tagopsBucket, tagopsSecret = authorize(request)
    limit = request.args.get("limit", LIMIT)
    offset = request.args.get("offset", OFFSET)
    rows = db.get_tag_list(limit, offset)
    response_list = []
    for row in rows:
        response_list.append(genrate_dict(TAG_FIELDS, row))
    if len(response_list):
        return jsonify(response_list), 200
    else:
        return jsonify({'messsage':"No data found"}), 200


def genrate_dict(fields, row):
    _dict = {}
    # if len(fields) != len(row):
    #     return
    
    for index in range(len(fields)):
        _dict[fields[index]] = row[index] if row[index] else ''

    return _dict 


@app.route("/users", methods=["POST"])
def create_user():
    res_json = request.data.decode('utf8').replace("'", '"')
    data = json.loads(res_json)
    data['tagopssecret'] = uuid.uuid4().hex
    data['tagopsbucket'] = uuid.uuid4().hex
    data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
    user_id = db.insert_user(data)
    if user_id:
        res = db.get_user(user_id[0])
        context = genrate_dict(USER_FIELDS, res)
        context['message'] = "User created!"
        return jsonify(context), 201
    else:
        return jsonify({'message':'User not created.'}), 500


@app.route("/users/<user_id>", methods=["GET"])
def user_details(user_id):
    tagopsBucket, tagopsSecret = authorize(request)
    res = db.get_user(user_id)
    response = {}
    if res:
        return jsonify(genrate_dict(USER_FIELDS, res)), 200
    else:
        return jsonify({'messsage':"No data found"}), 200


@app.route("/users/<user_id>", methods=["PATCH"])
def user_update(user_id):
    tagopsBucket, tagopsSecret = authorize(request)
    res_json = request.data.decode('utf8').replace("'", '"')
    data = json.loads(res_json)
    data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
    res = db.update_user(user_id, data)
    if res:
        res = db.get_user(user_id[0])
        context = genrate_dict(USER_FIELDS, res)
        context['message'] = "User Updated!"
        return jsonify(context), 201
    else:
        return jsonify({'message':'Something is missing!'}), 500


@app.route("/login", methods=["POST"])
def login():
    res_json = request.data.decode('utf8').replace("'", '"')
    data = json.loads(res_json)
    data['password'] = hashlib.md5(data['password'].encode('utf-8')).hexdigest()
    res = db.login(data)
    if res:
        res = db.get_user(res[0])
        tags.tagopsSecret = res[3]
        tags.tagopsBucket = res[4]
        context = genrate_dict(USER_FIELDS, res)
        context['message'] = "Successfully Loggedin!"
        return jsonify(context), 200
    else:
        return jsonify({'message': 'Email or password not matched!'}), 401


app.run(host="0.0.0.0", port=5000)