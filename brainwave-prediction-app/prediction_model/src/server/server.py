from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import time

from ..brain_reading import predictions

app = Flask(__name__)
socketio = SocketIO(app)

predictor = predictions.Predictor(125, .25)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('start_predicting')
def start_predicting():
    if predictor.is_predicting():
        emit('status', {'message': 'Already predicting.'})
        return
    predictor.start_predicting()
    socketio.start_background_task(background_thread)
    emit('status', {'message': 'Started predicting.'})


@socketio.on('stop_predicting')
def stop_predicting():
    predictor.stop_predicting()
    emit('status', {'message': 'Stopped predicting.'})


def background_thread():
    while not predictor.stop_event.is_set():
        time.sleep(.1)
        current_prediction = predictor.get_current_prediction()
        socketio.emit('new_prediction', {'prediction': current_prediction})


if __name__ == '__main__':
    # Suppress warnings for the sake of testing
    import warnings

    warnings.warn = lambda *args, **kwargs: None

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
