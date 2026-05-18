from flask import Flask, request, render_template, jsonify, Response
import mysql.connector
import json
from urllib.parse import urljoin
import requests

POC_ROOT = ''       #prefixul pentru pagina poc
API_ROOT = '/poc'    #prefixul pentru api-ul public
POC_PORT = 4999         #portul pe care va rula api-ul

LOCAL_API_ROOT = 'http://127.0.0.1:5000/'


app = Flask(__name__)

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

DB_CONFIG = read_json('POC/config.json')

'''
example POC/config.json:
{
    "mysql-host" : "127.0.0.1",
    "mysql-user" : "myuser",
    "mysql-pass" : "mypass",
    "mysql-database" : "mydb"
}
'''

@app.route(POC_ROOT + '/', methods=['GET'])
def proof_of_concept_main():
    if request.method == 'GET':
        return render_template("poc_index.html")
    else:
        return 'Method Not Allowed', 405


@app.route(API_ROOT + "/get_table/<table_name>", methods=["GET"])
def get_table(table_name):

    allowed_tables = [
        "solutions",
    ]

    if table_name not in allowed_tables:
        return jsonify({
            "error": "Invalid table"
        }), 400

    conn = mysql.connector.connect(**DB_CONFIG)

    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT *
        FROM {table_name}
        LIMIT 100
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)


@app.route(API_ROOT + "/<path:path>", methods=["POST"])
def proxy(path):
    # Build destination URL
    url = urljoin(LOCAL_API_ROOT + "/", path)

    # Get JSON payload
    json_data = request.get_json(silent=True)

    # Forward headers (remove unsafe ones)
    headers = {
        k: v for k, v in request.headers
        if k.lower() not in {
            "host",
            "content-length",
            "accept-encoding"
        }
    }

    # Forward POST request
    resp = requests.post(
        url,
        json=json_data,
        headers=headers,
        params=request.args,   # keep query string if any
        timeout=30
    )

    # Return upstream response
    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json")
    )

if __name__ == "__main__":
    app.run(port = POC_PORT, debug=True)
    exit()


