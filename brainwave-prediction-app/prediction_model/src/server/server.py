from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import time
import json

from ..brain_reading import models

app = Flask(__name__)
socketio = SocketIO(app)

predictor = models.Predictor(250, 1)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('start_predicting')
def start_predicting():
    predictor.start_predicting()
    socketio.start_background_task(background_thread)
    emit('status', {'message': 'Started predicting.'})


@socketio.on('stop_predicting')
def stop_predicting():
    predictor.stop_predicting()
    emit('status', {'message': 'Stopped predicting.'})


def background_thread():
    """Example of how to send server generated events to clients."""
    while not predictor.stop_event.is_set():
        time.sleep(.5)
        current_prediction = predictor.get_current_prediction()
        socketio.emit('new_prediction', {'prediction': json.dumps(current_prediction)})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
