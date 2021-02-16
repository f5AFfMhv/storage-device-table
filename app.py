#!/usr/bin/env python3

# Tutorials: 
# API with flask - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
# RESTful API with flask - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# Flask tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# Insert data to sqlite db - https://www.sqlitetutorial.net/sqlite-python/insert/
# HTML table filter example - https://morioh.com/p/51dbc30377fc

from flask import Flask, jsonify, request, make_response, send_file, redirect
from datetime import datetime
import sqlite3
import requests
import plotly.io as pio
import graphs # Script for creating graphs
import json
import pandas as pd

# Variables
BASE = 'http://localhost:5000'
API = '/api/v1/resources/servers' # API uri
BASE_URL = BASE + API
DB_FILE = 'servers.db'
HTML_TEMPLATE = 'html/index.html'
IFRAME_GRAPH = 'iframe_figures/figure_0.html'
TABLE_CONTENT_ORDER = ("id", "name", "ip", "device", "state", "size_gb", "free_gb", "used_perc", "updated", "delete")
STATE_COLOR = {'alert': 'red', 'warning': 'yellow', 'normal': 'lightgreen'}

app = Flask(__name__)
#app.config["DEBUG"] = True # Enable stdout logging

pio.renderers.default = "iframe" # How to render graphs

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
    return make_response(jsonify({'error':'Not found', 'status':e}), e)

def bad_request(e, msg=''):
    return make_response(jsonify({'error':'Bad request', 'status':e, 'message':msg}), e)

@app.errorhandler(404)
def default_page_not_found(e):
    return make_response(jsonify({'error':'Not found', 'status':404}), 404)

@app.errorhandler(400)
def default_bad_request(e):
    return make_response(jsonify({'error':'Bad request', 'status':400}), 400)

# Server root page shows table with all records from DB
@app.route('/', methods=['GET'])
def home():
    # Open table html template
    f = open(HTML_TEMPLATE,'r')
    server_table = f.read()
    # Make API call to get results for every state
    for device_state in STATE_COLOR:
        request = requests.get(BASE_URL + '?state=' + device_state)
        # Check if there is any device with state we are checking
        if request.status_code != 404:
            # Depending on current state, make table row with specified color background
            for record in request.json():
                server_table += '<tr style="background:' + STATE_COLOR.get(device_state) + ';">'
                # Place record data in TABLE_CONTENT_ORDER variable defined order
                for content in TABLE_CONTENT_ORDER:
                    # Add link to graph on device name
                    if content == "name":
                        server_table += '<td><a href=' + BASE + "/graph/" + str(record[content]) + ' target="_blank">' + str(record[content]) + '</a></td>'
                    # Add link to date coresponding record
                    elif content == "delete":
                        server_table += '<td><a href=' + BASE + "/remove/" + str(record["id"]) +\
                            '><img alt="DEL" src=' +  BASE +  '/delete.png width=20 height=20></a></td>'
                    # Add data from DB
                    else:
                        server_table += '<td>' + str(record[content]) + '</td>'
                server_table += '</tr>'
        else:
            pass

    # Add agent download links
    server_table += '</tbody></table><br><p>Downloads:</p>\
        <a href=' + BASE + '/download/linux_agent>➡️ Agent for linux</a>\
        <br><br>'
    # Add shameless plug
    server_table += '</body><br><footer><hr><a href=https://martynas.me target="_blank">Martynas J.</a> 2021</footer></html>'
    # Return html page with complete table
    return server_table

# Return host storage bar graph when clicked on hostname
@app.route('/graph/<name>', methods=['GET'])
def get_graph(name):
    # Generate graph with plotly as iframe
    fig = graphs.figure(BASE_URL, name)
    fig.create_graph().show()
    # Open graph iframe html 
    f = open(IFRAME_GRAPH,'r')
    graph = f.read()
    return graph

# Delete device from table
@app.route('/remove/<id>', methods=['GET'])
def delete(id):
    requests.delete(BASE_URL + '?id=' + id)
    return redirect(BASE, code=302)

# Allow to download agents
@app.route('/download/<agent>')
def download(agent):
    if agent == "linux_agent":
	    path = "scripts/disk_space.sh"
    else:
        return page_not_found(404)
    return send_file(path, as_attachment=True)

# Return file
@app.route('/<file>')
def file_return(file):
    if file == "favicon.ico":
	    path = "img/favicon.ico"
    elif file == "delete.png":
        path = "img/delete.png"
    elif file == "style.css":
        path = "html/style.css"
    elif file == "filter.js":
        path = "html/filter.js"
    elif file == "refresh_bar.js":
        path = "html/refresh_bar.js"
    else:
        return page_not_found(404)    
    return send_file(path, as_attachment=True)

# Generate CSV
@app.route('/export')
def export_table():
    request = requests.get(BASE_URL + '/all').json()
    export = pd.read_json(json.dumps(request))
    export.to_csv("SD_table.csv")
    return send_file("SD_table.csv", as_attachment=True)


# API OBTAIN INFORMATION
# Get all records from DB in JSON
@app.route(API + '/all', methods=['GET'])
def get_all_records():
    sql = ''' SELECT * FROM servers '''
    all_servers = db_read(DB_FILE, sql)
    return jsonify(all_servers)

# Get specific records from DB
@app.route(API, methods=['GET'])
def get_record():
    # Filter API requests by record ID, hostname, state or device
    id = request.args.get('id')
    state = request.args.get('state')
    name = request.args.get('name')
    device = request.args.get('device')

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
    if device:
        sql += ' device=? AND'
        to_filter.append(device)
    if not (id or state or name or device):
        return page_not_found(404)

    # Remove trailing 'AND' from sql query
    sql = sql[:-4]

    # Get results, if they exists, from DB
    results = db_read(DB_FILE, sql, to_filter)
    if results == []:
        return page_not_found(404)
    else:
        return jsonify(results)

# API CREATE NEW RESOURCE
# Create new server record. Record ID is incremented automaticaly by DB, so no need to pass record id
@app.route(API, methods=['POST'])
def create_record():

    # If POST request is valid, form list of arguments from request and add new record to DB file.
    # If value is missing NULL will be assigned
    if not request.json or not 'name' in request.json:
        return bad_request(400)
    # Check if request passed valid values for record
    if type(request.json.get('state')) != str or request.json.get('state') == None:
        return bad_request(400, 'state value incorect or missing')
    if type(request.json.get('size_gb')) != int or request.json.get('size_gb') == None:
        return bad_request(400, 'size_gb value incorect or missing')
    if type(request.json.get('free_gb')) != int or request.json.get('free_gb') == None:
        return bad_request(400, 'free_gb value incorect or missing')
    if type(request.json.get('used_perc')) != int or request.json.get('used_perc') == None:
        return bad_request(400, 'used_perc value incorect or missing')

    server_list = (request.json.get('name'), request.json.get('device'), request.json.get('state'), 
                    request.json.get('size_gb'), request.json.get('free_gb'), request.json.get('used_perc'), 
                    request.remote_addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # SQL query
    sql = ''' INSERT INTO servers(name,device,state,size_gb,free_gb,used_perc,ip,updated)
              VALUES(?,?,?,?,?,?,?,?) '''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)

    # Get latest record from DB
    sql = ''' SELECT * FROM servers WHERE id=(SELECT MAX(id) FROM servers); '''
    latest_server = db_read(DB_FILE, sql)
    return jsonify({'server': latest_server}), 201

# API UPDATE EXISTING RESOURCE
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
    # Check if request passed valid new values for record
    if type(request.json.get('state')) != str or request.json.get('state') == None:
        return bad_request(400, 'state value incorect or missing')
    if type(request.json.get('size_gb')) != int or request.json.get('size_gb') == None:
        return bad_request(400, 'size_gb value incorect or missing')
    if type(request.json.get('free_gb')) != int or request.json.get('free_gb') == None:
        return bad_request(400, 'free_gb value incorect or missing')
    if type(request.json.get('used_perc')) != int or request.json.get('used_perc') == None:
        return bad_request(400, 'used_perc value incorect or missing')

    # Form list of new values from request (no NULL values should be added, because of previous check)
    server_list = (request.json.get('state'), request.json.get('size_gb'), request.json.get('free_gb'),
        request.json.get('used_perc'), request.remote_addr, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.json.get('id'))
   
    # Build SQL query
    sql = ''' UPDATE servers
              SET state = ? ,
                  size_gb = ? ,
                  free_gb = ? ,
                  used_perc = ?,
                  ip = ?,
                  updated = ?
              WHERE id = ?'''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)
    # Get modified record from DB
    r = requests.get(BASE_URL + '?id=' + str(id))
    return jsonify({'server': r.json()})

# API DELETE RECORD
# Delete existing record from DB file
@app.route(API, methods=['DELETE'])
def delete_record():
    # Check if record exists
    id = request.args.get('id')
    r = requests.get(BASE_URL + '?id=' + id)
    if (r.status_code == 404):
        return page_not_found(404)
    
    # Form SQL query
    sql = ''' DELETE FROM servers WHERE id=? '''
    # Execute SQL query
    db_mod(DB_FILE, sql, (id,))
    return jsonify({'result': True}), 200

app.run(host='0.0.0.0')
