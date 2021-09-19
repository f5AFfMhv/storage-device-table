#!/usr/bin/env python3

"""
This application is RESTful API for monitoring storage device usage.
Application is made using Flask. Apart from API this application renders HTML table with all records in the internal
SQLite DB file using API calls.
For more information how to use API check this project Github page
https://github.com/f5AFfMhv/storage-device-table


Copyright (C) 2021 Martynas J.
f5AFfMhv@protonmail.com
https://github.com/f5AFfMhv

Tutorials: 
    API with flask - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    RESTful API with flask - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
    Flask tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
    Insert data to sqlite db - https://www.sqlitetutorial.net/sqlite-python/insert/
    Flask render JINJA template - https://hackersandslackers.com/flask-jinja-templates/
"""

import json
import requests
from flask import Flask, jsonify, request, make_response, send_file, redirect, render_template
from datetime import datetime
import sqlite3
import plotly.io as pio
import graphs  # Script for creating graphs
import pandas as pd

# Variables
PORT = 5000
BASE = 'http://localhost:' + str(PORT)
API = '/api/v1/devices'  # API uri
BASE_URL = BASE + API
DB_FILE = 'SDT.db'
IFRAME_GRAPH = 'iframe_figures/figure_0.html'
STATE_ORDER = ["alert", "warning", "normal"]
CSV_EXPORT_ORDER = ['id', 'host', 'ip', 'device',
                    'state', 'size_mb', 'free_mb', 'used_perc', 'updated']
VERSION = "v1.2"

app = Flask(__name__)
# app.config["DEBUG"] = True # Enable stdout logging

pio.renderers.default = "iframe"  # Graph rendering method

# Function to convert data from SQLite DB to dictionary (from "API with flask" tutorial)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Function to read and parse data from SQLite DB
def db_read(db, sql, opts=''):
    conn = sqlite3.connect(db)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    return cur.execute(sql, opts).fetchall()

# Function to modify SQLite DB data
def db_mod(db, sql, opts=''):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql, opts)
    conn.commit()

# Error handling functions
def page_not_found(e):
    return make_response(jsonify({'error': 'Not found', 'status': e}), e)


def bad_request(e, msg=''):
    return make_response(jsonify({'error': 'Bad request', 'status': e, 'message': msg}), e)


@app.errorhandler(404)
def default_page_not_found(e):
    return make_response(jsonify({'error': 'Not found', 'status': 404}), 404)


@app.errorhandler(400)
def default_bad_request(e):
    return make_response(jsonify({'error': 'Bad request', 'status': 400}), 400)


# Server root page shows table with all records from DB
@app.route('/', methods=['GET'])
def home():
    row = []  # List of table rows to be rendered
    for device_state in STATE_ORDER:
        # Make API call to get results for every state individualy
        request = requests.get(BASE_URL + '?state=' + device_state)
        # Is there any device with state we are checking?
        if request.status_code != 404:
            # Collect information for table row render
            data = request.json()
            # Combine all information into one list of rows
            row.extend(data)
    return render_template('table.html', row=row, query="Search query ...", version=VERSION)

# Return host storage bar graph when clicked on hostname
@app.route('/graph/<name>', methods=['GET'])
def get_graph(name):
    # Generate graph with plotly as iframe
    fig = graphs.figure(BASE_URL, name)
    fig.create_graph().show()
    # Open graph iframe html
    f = open(IFRAME_GRAPH, 'r')
    graph = f.read()
    return graph

# Render search results to table.html
@app.route('/search', methods=['GET'])
def search():
    row = []  # List of table rows to be rendered
    query = request.args.get('search_text')
    # If search query is empty return full table
    if query == "":
        return home()
    else:
        # Make API call to get results for matching name
        r = requests.get(BASE_URL + '/all')
        data = r.json()
        # Search for query in each record all value fields
        for record in data:
            # Flag for prevent duplicates
            appended = False
            for col in CSV_EXPORT_ORDER:
                # If match found and record is not already appended, add it to an array
                if query in str(record.get(col)) and not appended:
                    row.append(record)
                    appended = True
        # Render table.html template with search results
        return render_template('table.html', row=row, query="Search: " + query, version=VERSION)

# Delete device from table
@app.route('/remove/<id>', methods=['GET'])
def delete(id):
    requests.delete(BASE_URL + '?id=' + id)
    return redirect("../", code=302)

# Allow to download agents
@app.route('/download/<agent>')
def download(agent):
    if agent == "linux_agent":
        path = "scripts/SDT-linux-agent.sh"
    elif agent == "windows_agent":
        path = "scripts/SDT-windows-agent.ps1"
    elif agent == "ansible_playbook":
        path = "scripts/SDT-ansible-playbook.yml"
    elif agent == "deploy_playbook":
        path = "scripts/deploy-linux-agent.yml"
    else:
        return page_not_found(404)
    return send_file(path, as_attachment=True)

# Return various files for HTML page rendering
@app.route('/<file>')
def file_return(file):
    if file == "favicon.ico":
        path = "img/favicon.ico"
    elif file == "delete.png":
        path = "img/delete.png"
    elif file == "style.css":
        path = "templates/style.css"
    elif file == "sort.js":
        path = "templates/sort.js"
    elif file == "reload.js":
        path = "templates/reload.js"
    else:
        return page_not_found(404)
    return send_file(path, as_attachment=True)


# Generate CSV from all records in database
@app.route('/export')
def export_table():
    # Request all records from API
    request = requests.get(BASE_URL + '/all').json()
    # Generate CSV using pandas module
    export = pd.read_json(json.dumps(request))
    export.to_csv("SD_table.csv", index=False, columns=CSV_EXPORT_ORDER)
    return send_file("SD_table.csv", as_attachment=True)


# Code below implements RESTful API functionality
#                                                               OBTAIN INFORMATION
#
# Get all records from DB in JSON
@app.route(API + '/all', methods=['GET'])
def get_all_records():
    sql = ''' SELECT * FROM devices '''
    all_devices = db_read(DB_FILE, sql)
    return jsonify(all_devices)

# Get specific records from DB


@app.route(API, methods=['GET'])
def get_record():
    # Filter API requests by record ID, hostname, state or device
    id = request.args.get('id')
    state = request.args.get('state')
    host = request.args.get('host')
    device = request.args.get('device')

    # Build SQL query from given requests
    sql = "SELECT * FROM devices WHERE"
    to_filter = []

    if id:
        sql += ' id=? AND'
        to_filter.append(id)
    if state:
        sql += ' state=? AND'
        to_filter.append(state)
    if host:
        sql += ' host=? AND'
        to_filter.append(host)
    if device:
        sql += ' device=? AND'
        to_filter.append(device)
    if not (id or state or host or device):
        return page_not_found(404)

    # Remove trailing 'AND' from sql query
    sql = sql[:-4]

    # Get results, if they exists, from DB
    results = db_read(DB_FILE, sql, to_filter)
    if results == []:
        return page_not_found(404)
    else:
        return jsonify(results)

#                                                               CREATE NEW RESOURCE
#
# Create new server record. Record ID is incremented automaticaly by DB, so no need to pass record id
@app.route(API, methods=['POST'])
def create_record():

    print(request.json)
    # If POST request is valid, form list of arguments from request and add new record to DB file.
    # If value is missing NULL will be assigned
    if not request.json or not 'host' in request.json:
        return bad_request(400)

    server_list = (request.json.get('host'), request.json.get('device'), request.json.get('state'),
                   request.json.get('size_mb'), request.json.get(
                       'free_mb'), request.json.get('used_perc'),
                   request.remote_addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # SQL query
    sql = ''' INSERT INTO devices(host,device,state,size_mb,free_mb,used_perc,ip,updated)
              VALUES(?,?,?,?,?,?,?,?) '''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)

    # Get latest record from DB
    sql = ''' SELECT * FROM devices WHERE id=(SELECT MAX(id) FROM devices); '''
    latest_server = db_read(DB_FILE, sql)
    return jsonify({'server': latest_server}), 201

#                                                           UPDATE EXISTING RESOURCE
#
# Update existing record by id with new values (can't change server name or device)
@app.route(API, methods=['PUT'])
def update_record():
    # Check request validity
    if not request.json or not 'id' in request.json:
        return bad_request(400, 'id value incorect or missing')
    # Check if record with provided id exists in DB
    id = request.json.get('id')
    r = requests.get(BASE_URL + '?id=' + str(id))
    if (r.status_code == 404):
        return page_not_found(404)

    # Form list of new values from request (no NULL values should be added, because of previous check)
    server_list = (request.json.get('state'), request.json.get('size_mb'), request.json.get('free_mb'),
                   request.json.get('used_perc'), request.remote_addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.json.get('id'))

    # Build SQL query
    sql = ''' UPDATE devices
              SET state = ? ,
                  size_mb = ? ,
                  free_mb = ? ,
                  used_perc = ?,
                  ip = ?,
                  updated = ?
              WHERE id = ?'''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)
    # Get modified record from DB
    r = requests.get(BASE_URL + '?id=' + str(id))
    return jsonify({'server': r.json()})

#                                                               DELETE RECORD
#
# Delete existing record from DB file
@app.route(API, methods=['DELETE'])
def delete_record():
    # Check if record exists
    id = request.args.get('id')
    r = requests.get(BASE_URL + '?id=' + id)
    if (r.status_code == 404):
        return page_not_found(404)

    # Form SQL query
    sql = ''' DELETE FROM devices WHERE id=? '''
    # Execute SQL query
    db_mod(DB_FILE, sql, (id,))
    return jsonify({'result': True}), 200


app.run(host='0.0.0.0', port=PORT)

