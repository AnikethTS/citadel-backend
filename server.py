from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

messages_file = 'messages.json'

def load_messages():
    if os.path.exists(messages_file):
        with open(messages_file, 'r') as f:
            return json.load(f)
    else:
        return []

def save_all_messages(messages):
    with open(messages_file, 'w') as f:
        json.dump(messages, f, indent=4)

def save_message(new_message):
    messages = load_messages()
    messages.append(new_message)
    save_all_messages(messages)

@app.route('/')
def index():
    return "Citadel Messaging Server is Live!"

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(load_messages())

@socketio.on('send_message')
def handle_send_message(data):
    save_message(data)
    emit('receive_message', data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', data, broadcast=True)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    emit('stop_typing', data, broadcast=True)

# 💥 Admin Edit Message
@socketio.on('edit_message')
def handle_edit_message(data):
    index = data.get('index')
    new_message = data.get('new_message')
    messages = load_messages()
    if 0 <= index < len(messages):
        messages[index]['message'] = new_message
        save_all_messages(messages)
        emit('update_messages', messages, broadcast=True)

# 🗑️ Admin Delete Message
@socketio.on('delete_message')
def handle_delete_message(data):
    index = data.get('index')
    messages = load_messages()
    if 0 <= index < len(messages):
        del messages[index]
        save_all_messages(messages)
        emit('update_messages', messages, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
