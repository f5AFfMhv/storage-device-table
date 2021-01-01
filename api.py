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


app = Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def page_not_found(e):
    return make_response(jsonify({'error': 'Not found'}), e)

def bad_request(e):
    return make_response(jsonify({'error': 'Bad request'}), e)

@app.route('/', methods=['GET'])
def home():
    #return "<h1>Server disk usage table</h1>"
    r = requests.get('http://localhost:5000/api/v1/resources/servers/all')
    return json2html.convert(json = r.json())

@app.route('/api/v1/resources/servers/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('servers.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_servers = cur.execute('SELECT * FROM servers;').fetchall()
    return jsonify(all_servers)

@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1/resources/servers', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    state = query_parameters.get('state')
    name = query_parameters.get('name')

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

@app.route('/api/v1/resources/servers', methods=['POST'])
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

@app.route('/api/v1/resources/servers', methods=['DELETE'])
def delete_record():
    query_parameters = request.args
    id = query_parameters.get('id')
    r = requests.get('http://localhost:5000/api/v1/resources/servers?id=' + id)
    if (r.status_code == 404):
        return bad_request(400)
    
    sql = ''' DELETE FROM servers WHERE id=? '''
    conn = sqlite3.connect('servers.db')
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()
    return jsonify({'result': True}), 200

@app.route('/api/v1/resources/servers', methods=['PUT'])
def update_record():
    if not request.json or not 'id' in request.json:
        return bad_request(400)
    id = request.json.get('id')
    r = requests.get('http://localhost:5000/api/v1/resources/servers?id=' + str(id))
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
    r = requests.get('http://localhost:5000/api/v1/resources/servers?id=' + str(id))
    return jsonify({'server': r.json()})
    
app.run(host='0.0.0.0')
