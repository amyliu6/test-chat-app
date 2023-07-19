# server.py

from flask import Flask, render_template
from flask_socketio import SocketIO
from time import time
from openAI import sendMsgToChatGPT

app = Flask(__name__)
socket_io = SocketIO(app, cors_allowed_origins="*")

@socket_io.on('connect')
def handle_connect():
    print('new connection')

@socket_io.on('to-server')
def handle_to_server(messages):
    # print(f'new to-server event: {msgObj}')

    model_message = sendMsgToChatGPT(messages)
        
    socket_io.emit('from-server', model_message)

if __name__ == '__main__':
    socket_io.run(app, port=50000)