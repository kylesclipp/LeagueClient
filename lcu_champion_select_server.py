from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import base64
import psutil
import os
import json
import urllib3

app = Flask(__name__)
CORS(app)

# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_lockfile_data():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'LeagueClientUx.exe':
            lockfile_path = os.path.join(os.path.dirname(proc.exe()), 'lockfile')
            with open(lockfile_path, 'r') as lockfile:
                data = lockfile.read().split(':')
                return {
                    'process_name': data[0],
                    'pid': data[1],
                    'port': data[2],
                    'password': data[3],
                    'protocol': data[4]
                }
    raise Exception("League Client is not running")

def get_request_headers(password):
    userpass = f'riot:{password}'
    encoded_userpass = base64.b64encode(userpass.encode()).decode()
    return {
        'Authorization': f'Basic {encoded_userpass}'
    }

@app.route('/')
def serve_frontend():
    return send_file('champion_select_control.html')

@app.route('/champion-select', methods=['GET'])
def get_champion_select():
    try:
        lockfile_data = get_lockfile_data()
        headers = get_request_headers(lockfile_data['password'])
        response = requests.get(
            f"https://127.0.0.1:{lockfile_data['port']}/lol-champ-select/v1/session",
            headers=headers,
            verify=False
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pick-champion', methods=['POST'])
def pick_champion():
    try:
        data = request.json
        champion_id = data.get('championId')
        action_id = data.get('actionId')
        
        lockfile_data = get_lockfile_data()
        headers = get_request_headers(lockfile_data['password'])
        response = requests.patch(
            f"https://127.0.0.1:{lockfile_data['port']}/lol-champ-select/v1/session/actions/{action_id}",
            headers=headers,
            json={
                'championId': champion_id,
                'completed': True
            },
            verify=False
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ban-champion', methods=['POST'])
def ban_champion():
    try:
        data = request.json
        champion_id = data.get('championId')
        action_id = data.get('actionId')
        
        lockfile_data = get_lockfile_data()
        headers = get_request_headers(lockfile_data['password'])
        response = requests.patch(
            f"https://127.0.0.1:{lockfile_data['port']}/lol-champ-select/v1/session/actions/{action_id}",
            headers=headers,
            json={
                'championId': champion_id,
                'completed': True
            },
            verify=False
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)