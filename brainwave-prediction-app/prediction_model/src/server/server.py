from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import time

from ..brain_reading import recorder, headsets
from ..data_processing import config

app = Flask(__name__, template_folder='templates', static_folder='static')
socketio = SocketIO(app)

# predictor = predictions.Predictor(125, .25)
recorder = recorder.BrainwaveRecorder(125, 'recordings')
sim_headset = headsets.SyntheticHeadsetStreamer(config.headset_streaming_host, config.headset_streaming_port)
socketio.start_background_task(sim_headset.start_stream)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict')
def predict():
    return render_template('training_session.html')


@socketio.on('start_recording')
def start_recording(data):
    # print('Starting recording')
    # print(f'Duration: {duration}')
    # print(f'Instruction: {instruction}')
    instruction = data['instruction']
    duration = data['duration']
    label = instruction['label']
    session = data['session']
    round = data['round']
    socketio.start_background_task(wait_for_recording, int(duration), label, session, round)


def wait_for_recording(duration: int, label, session, round):
    df = recorder.record(duration, label)
    print('Recording complete')
    print(f'lag: {time.time() - df.loc[df.index[0], " Timestamp"]}')
    print(df.loc[df.index[-1], ' Timestamp'] - df.loc[0, ' Timestamp'])
    socketio.emit('stop_recording')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True, use_reloader=False)
