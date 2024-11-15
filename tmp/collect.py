from flask import Flask, request, jsonify
import signal
import sys
import json


app = Flask(__name__)
durations = []

@app.route('/post_duration', methods=['POST'])
def post_duration():
    data = request.get_json()
    if 'duration' in data and isinstance(data['duration'], float):
        durations.append(data['duration'])
        print(f"{data['duration']} added to durations")
        return jsonify({"message": "Duration added"}), 200
    else:
        return jsonify({"error": "Invalid input"}), 400

def signal_handler(sig, frame):
    with open('durations.json', 'w') as f:
        json.dump(durations, f)
    print('Durations saved to durations.json')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)