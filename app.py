from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client["github_webhooks"]
collection = db["events"]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {'_id': 0}).sort("timestamp", -1).limit(10))
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    payload = {}

    if event_type == "push":
        payload = {
            "type": "PUSH",
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
            "timestamp": datetime.utcnow()
        }
    elif event_type == "pull_request":
        pr = data['pull_request']
        if data['action'] == "opened":
            payload = {
                "type": "PULL_REQUEST",
                "author": pr['user']['login'],
                "from_branch": pr['head']['ref'],
                "to_branch": pr['base']['ref'],
                "timestamp": datetime.utcnow()
            }
        elif data['action'] == "closed" and pr.get('merged'):
            payload = {
                "type": "MERGE",
                "author": pr['user']['login'],
                "from_branch": pr['head']['ref'],
                "to_branch": pr['base']['ref'],
                "timestamp": datetime.utcnow()
            }

    if payload:
        collection.insert_one(payload)
        return jsonify({"msg": "stored"}), 200

    return jsonify({"msg": "ignored"}), 200

if __name__ == '__main__':
    app.run(port=5000)
