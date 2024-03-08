from flask import Flask, jsonify, request
import subprocess
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import socket
import requests
import re

app = Flask(__name__, static_folder='static')

logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

hosts_status = {}
hosts_status_lock = threading.Lock()

DISCORD_WEBHOOK_URL = "YOUR-DISCORD-WEBHOOK-URL"

def send_discord_notification(host, message):
    if hosts_status.get(host, {}).get('notifications_enabled', False):
        data = {"content": message}
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=data)
            if response.status_code != 204:
                logging.error(f"Failed to send notification to Discord for {host}. Status code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"ConnectionError while sending notification to Discord for {host}: {e}")

def ping_host(host):
    param = '-n' if subprocess.os.name == 'nt' else '-c'
    command = ['ping', param, '1', host]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        match = re.search(r'(temps|time)[=<](\d+\.?\d*) ?ms', result.stdout)
        if match:
            response_time = float(match.group(2))
            return 'OK', response_time
        elif "temps<1ms" in result.stdout or "time<1ms" in result.stdout:
            return 'OK', 0.5
        elif "octets=" in result.stdout or "bytes=" in result.stdout:
            return 'OK', None
        else:
            return 'KO', None
    except subprocess.CalledProcessError:
        return 'KO', None

def update_host_status():
    while True:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            with hosts_status_lock:
                for host, info in hosts_status.items():
                    futures.append(executor.submit(check_and_update_host, host, info))
            for future in futures:
                future.result()
            time.sleep(10)

def check_and_update_host(host, info):
    current_status, response_time = ping_host(host)
    with hosts_status_lock:
        if current_status != info['status']:
            info['status'] = current_status
            info['last_change'] = time.time()
            if info['notifications_enabled']:
                status_change_msg = f"Host {info['label']} ({host}) status changed to {current_status}"
                send_discord_notification(host, status_change_msg)
        info['last_check'] = time.time()
        if current_status == 'OK':
            info['response_time'] = response_time

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/status')
def status():
    with hosts_status_lock:
        for host, info in hosts_status.items():
            if info['status'] == 'OK':
                info['up_duration'] = time.time() - info['last_change']
                info['down_duration'] = 0
            else:
                info['down_duration'] = time.time() - info['last_change']
                info['up_duration'] = 0
    return jsonify(hosts_status)

@app.route('/add_host', methods=['POST'])
def add_host():
    data = request.json
    with hosts_status_lock:
        hosts_status[data['host']] = {
            'label': data.get('label', 'No Label'),
            'status': 'Unknown',
            'last_change': time.time(),
            'up_duration': 0,
            'down_duration': 0,
            'notifications_enabled': data.get('notifications_enabled', True),
            'response_time': None
        }
    return jsonify({'message': 'Host added successfully'})

@app.route('/remove_host', methods=['POST'])
def remove_host():
    data = request.json
    with hosts_status_lock:
        if data['host'] in hosts_status:
            del hosts_status[data['host']]
            return jsonify({'message': 'Host removed successfully'})
        else:
            return jsonify({'error': 'Host not found'}), 404

@app.route('/toggle_notifications', methods=['POST'])
def toggle_notifications():
    data = request.json
    with hosts_status_lock:
        if data['host'] in hosts_status:
            hosts_status[data['host']]['notifications_enabled'] = not hosts_status[data['host']]['notifications_enabled']
            return jsonify({'message': 'Notification state toggled', 'notifications_enabled': hosts_status[data['host']]['notifications_enabled']})
        else:
            return jsonify({'error': 'Host not found'}), 404

@app.route('/clear_hosts', methods=['POST'])
def clear_hosts():
    with hosts_status_lock:
        hosts_status.clear()
    return jsonify({'message': 'All hosts have been cleared successfully'})

if __name__ == '__main__':
    threading.Thread(target=update_host_status, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')
