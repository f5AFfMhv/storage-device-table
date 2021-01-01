#!/usr/bin/env python3

# Tutorials: 
# API with flask - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
# RESTful API with flask - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# Flask tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# Insert data to sqlite db - https://www.sqlitetutorial.net/sqlite-python/insert/

from flask import Flask, jsonify, request, make_response
from json2html import *
import sqlite3
import requests

# Variables
BASE = '/api/v1/resources/servers' # API uri
BASE_URL = 'http://localhost:5000' + BASE
DB_FILE = 'servers.db'

app = Flask(__name__)
app.config["DEBUG"] = True # Enable stdout logging

# Method to convert data from SQLite DB to dictionary (from "API with flask" tutorial)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Method to read and parse data from SQLite DB
def db_read(db, sql):
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    return cur.execute(sql).fetchall()

# Error handling methods
def page_not_found(e):
    return make_response(jsonify({'error':'Not found', 'status':e}), e)

def bad_request(e):
    return make_response(jsonify({'error':'Bad request', 'status':e}), e)

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({'error':'Not found', 'status':404}), 404)

# Server root page shows table with all records from DB
@app.route('/', methods=['GET'])
def home():
    # Get data from API
    r = requests.get(BASE_URL + '/all')
    # Result --> JSON --> HTML
    return json2html.convert(json = r.json())

# API OBTAIN INFORMATION
# Get all records from DB in JSON
@app.route(BASE + '/all', methods=['GET'])
def get_all_records():
    sql = ''' SELECT * FROM servers '''
    all_servers = db_read(DB_FILE, sql)
    return jsonify(all_servers)

# Get specific records from DB
@app.route(BASE, methods=['GET'])
def get_record():
    # Filter API requests by record ID, name or state
    id = request.args.get('id')
    state = request.args.get('state')
    name = request.args.get('name')

    # Build SQL query from given requests
    sql = "SELECT * FROM servers WHERE"
    to_filter = []

    if id:
        sql += ' id=? AND'
        to_filter.append(id)
    if state:
        sql += ' state=? AND'
        to_filter.append(state)
    if name:
        sql += ' name=? AND'
        to_filter.append(name)
    if not (id or state or name):
        return page_not_found(404)

    sql = sql[:-4] + ';'

    conn = sqlite3.connect('servers.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(sql, to_filter).fetchall()
    if results == []:
        return page_not_found(404)
    else:
        return jsonify(results)

@app.route(BASE, methods=['POST'])
def create_record():

    if not request.json or not 'name' in request.json:
        return bad_request(400)
    server = {
        'name' : request.json.get('name'),
        'mount' : request.json.get('mount'),
        'state' : request.json.get('state'),
        'size_gb' : request.json.get('size_gb'),
        'free_gb' : request.json.get('free_gb'),
        'used_perc' : request.json.get('used_perc')
    }

    server_list = (request.json.get('name'), request.json.get('mount'), request.json.get('state'), 
                    request.json.get('size_gb'), request.json.get('free_gb'), request.json.get('used_perc'))
    
    sql = ''' INSERT INTO servers(name,mount,state,size_gb,free_gb,used_perc)
              VALUES(?,?,?,?,?,?) '''

    conn = sqlite3.connect('servers.db')
    cur = conn.cursor()
    cur.execute(sql, server_list)
    conn.commit()
    return jsonify({'server': server}), 201

@app.route(BASE, methods=['DELETE'])
def delete_record():
    query_parameters = request.args
    id = query_parameters.get('id')
    r = requests.get(BASE_URL + '?id=' + id)
    if (r.status_code == 404):
        return bad_request(400)
    
    sql = ''' DELETE FROM servers WHERE id=? '''
    conn = sqlite3.connect('servers.db')
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    return jsonify({'result': True}), 200

@app.route(BASE, methods=['PUT'])
def update_record():
    if not request.json or not 'id' in request.json:
        return bad_request(400)
    id = request.json.get('id')
    r = requests.get(BASE_URL + '?id=' + str(id))
    if (r.status_code == 404):
        return bad_request(400)
    if 'state' in request.json and type(request.json['state']) != str:
        return bad_request(400)
    if 'size_gb' in request.json and type(request.json['size_gb']) != int:
        return bad_request(400)
    if 'free_gb' in request.json and type(request.json['free_gb']) != int:
        return bad_request(400)
    if 'used_perc' in request.json and type(request.json['used_perc']) != int:
        return bad_request(400)

    server_list = (request.json.get('state'), request.json.get('size_gb'), request.json.get('free_gb'), request.json.get('used_perc'), request.json.get('id'))

    sql = ''' UPDATE servers
              SET state = ? ,
                  size_gb = ? ,
                  free_gb = ? ,
                  used_perc = ?
              WHERE id = ?'''
    conn = sqlite3.connect('servers.db')
    cur = conn.cursor()
    cur.execute(sql, server_list)
    conn.commit()
    r = requests.get(BASE_URL + '?id=' + str(id))
    return jsonify({'server': r.json()})
    
app.run(host='0.0.0.0')
