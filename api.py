#!/usr/bin/env python3

# Tutorials: 
# API with flask - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask


from flask import Flask, jsonify, request
import sqlite3


app = Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/', methods=['GET'])
def home():
    return "<h1>Server disk usage table</h1>"

@app.route('/api/v1/resources/servers/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('servers.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_servers = cur.execute('SELECT * FROM servers;').fetchall()

    return jsonify(all_servers)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v1/resources/servers', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    state = query_parameters.get('state')
    name = query_parameters.get('name')

    query = "SELECT * FROM servers WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if state:
        query += ' state=? AND'
        to_filter.append(state)
    if name:
        query += ' name=? AND'
        to_filter.append(name)
    if not (id or state or name):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('servers.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()