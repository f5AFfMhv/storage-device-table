#!/usr/bin/env python3

# Tutorials: 
# API with flask - https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
# RESTful API with flask - https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# Flask tutorial - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# Insert data to sqlite db - https://www.sqlitetutorial.net/sqlite-python/insert/
# HTML filter table example - https://morioh.com/p/51dbc30377fc

from flask import Flask, jsonify, request, make_response
import sqlite3
import requests

# Variables
BASE = '/api/v1/resources/servers' # API uri
BASE_URL = 'http://localhost:5000' + BASE
DB_FILE = 'servers.db'
HTML_TEMPLATE = 'html/table.html'

app = Flask(__name__)
app.config["DEBUG"] = True # Enable stdout logging

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
    # Get data from API
    r = requests.get(BASE_URL + '/all')
    all_servers = r.json()
    # Open html template
    f = open(HTML_TEMPLATE,'r')
    server_table = f.read()
    server_table_normal = ''
    server_table_warning = ''
    server_table_alert = ''
    server_table_other = ''
    # Add data from API call. Also make some filtering that records with alert state would be on top
    for i in all_servers:
        if i['state'] == "normal":
            server_table_normal += '<tr style="background:lightgreen;"><td>' + str(i['id']) + \
                        '</td><td>' + str(i['name']) + \
                        '</td><td>' + str(i['mount']) + \
                        '</td><td>' + str(i['state']) + \
                        '</td><td>' + str(i['size_gb']) + \
                        '</td><td>' + str(i['free_gb']) + \
                        '</td><td>' + str(i['used_perc']) + \
                        '</td></tr>'
        elif i['state'] == "warning":
            server_table_warning += '<tr style="background:yellow;"><td>' + str(i['id']) + \
                        '</td><td>' + str(i['name']) + \
                        '</td><td>' + str(i['mount']) + \
                        '</td><td>' + str(i['state']) + \
                        '</td><td>' + str(i['size_gb']) + \
                        '</td><td>' + str(i['free_gb']) + \
                        '</td><td>' + str(i['used_perc']) + \
                        '</td></tr>'
        elif i['state'] == "alert":
            server_table_alert += '<tr style="background:red;"><td>' + str(i['id']) + \
                        '</td><td>' + str(i['name']) + \
                        '</td><td>' + str(i['mount']) + \
                        '</td><td>' + str(i['state']) + \
                        '</td><td>' + str(i['size_gb']) + \
                        '</td><td>' + str(i['free_gb']) + \
                        '</td><td>' + str(i['used_perc']) + \
                        '</td></tr>'
        else:
            server_table_other += '<tr><td>' + str(i['id']) + \
                        '</td><td>' + str(i['name']) + \
                        '</td><td>' + str(i['mount']) + \
                        '</td><td>' + str(i['state']) + \
                        '</td><td>' + str(i['size_gb']) + \
                        '</td><td>' + str(i['free_gb']) + \
                        '</td><td>' + str(i['used_perc']) + \
                        '</td></tr>'
        
    server_table += server_table_alert + server_table_warning + server_table_normal + server_table_other +'</tbody></table><p>by Martynas J.</p></body></html>' 
    return server_table

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
@app.route(BASE, methods=['POST'])
def create_record():

    # If POST request is valid, form list of arguments from request and add new record to DB file.
    # If value is missing NULL will be assigned
    if not request.json or not 'name' in request.json:
        return bad_request(400)

    server_list = (request.json.get('name'), request.json.get('mount'), request.json.get('state'), 
                    request.json.get('size_gb'), request.json.get('free_gb'), request.json.get('used_perc'))
    # SQL query
    sql = ''' INSERT INTO servers(name,mount,state,size_gb,free_gb,used_perc)
              VALUES(?,?,?,?,?,?) '''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)

    # Get latest record from DB
    sql = ''' SELECT * FROM servers WHERE id=(SELECT MAX(id) FROM servers); '''
    latest_server = db_read(DB_FILE, sql)
    return jsonify({'server': latest_server}), 201

# API UPDATE EXISTING RESOURCE
# Update existing record by id with new values (can't change server name or mount point)
@app.route(BASE, methods=['PUT'])
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
    server_list = (request.json.get('state'), request.json.get('size_gb'), request.json.get('free_gb'), request.json.get('used_perc'), request.json.get('id'))

    # Build SQL query
    sql = ''' UPDATE servers
              SET state = ? ,
                  size_gb = ? ,
                  free_gb = ? ,
                  used_perc = ?
              WHERE id = ?'''

    # Execute SQL query
    db_mod(DB_FILE, sql, server_list)
    # Get modified record from DB
    r = requests.get(BASE_URL + '?id=' + str(id))
    return jsonify({'server': r.json()})

# API DELETE RECORD
# Delete existing record from DB file
@app.route(BASE, methods=['DELETE'])
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
