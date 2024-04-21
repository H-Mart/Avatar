import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

from .headsets import get_listening_socket
from ..data_processing import config

from threading import Thread, Event
import socket
import time

HEADSET_DATA_LENGTH_BYTES = 256
HEADSET_DATA_LENGTH_FLOATS = 32

RELEVANT_COLS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30)


class Predictor:
    def __init__(self, sampling_rate, period=1):
        self.sock = get_listening_socket(config.headset_streaming_host, config.headset_streaming_port)
        self.model = load_model(200, None, 'gini')
        self.model.verbose = 0

        self.pred_buffer = np.zeros(int(sampling_rate * period), dtype=np.int16)
        self.sample_buffer = np.empty(32 * config.brainflow_batch_size, dtype=np.float64)

        self.label_map = ['forward', 'land', 'takeoff', 'backward', 'left', 'right']

        self.stop_event = Event()
        self.prediction_thread = None

    def get_current_prediction(self):
        bins = np.bincount(self.pred_buffer, minlength=6) / len(self.pred_buffer)
        return {l: bins[i] for i, l in enumerate(self.label_map)}

    def start_predicting(self):
        print('starting prediction')
        self.stop_event.clear()
        self.prediction_thread = self._make_thread()
        self.prediction_thread.start()

    def stop_predicting(self):
        print('ending prediction')
        self.stop_event.set()
        self.prediction_thread.join()
        self.prediction_thread = None

    def is_predicting(self):
        return not self.stop_event.is_set() and self.prediction_thread is not None

    def _make_thread(self):
        return Thread(target=self._connect_socket_to_model)

    def _connect_socket_to_model(self):
        i = 0
        delta = lambda t: time.time() - t

        pred_buf_len = len(self.pred_buffer)
        last = time.time()
        while not self.stop_event.is_set():
            try:
                nbytes, address = self.sock.recvfrom_into(self.sample_buffer)
            except socket.timeout:
                print('connection timeout')
                continue

            num_rows = nbytes // HEADSET_DATA_LENGTH_BYTES
            data = (self.sample_buffer[:num_rows * HEADSET_DATA_LENGTH_FLOATS]
                    .reshape((num_rows, HEADSET_DATA_LENGTH_FLOATS))[:, RELEVANT_COLS])

            # stats
            dt = delta(last)
            last = time.time()
            actual_sample_rate = num_rows / dt
            average_sample_rate = 1 / (data[1:, -1] - data[:-1, -1]).mean()

            # todo want to turn this into something that can be sent to the client
            print(f'got {nbytes} bytes in {dt * 1000:.2f} ms, rt lag: {(last - data[-1, -1]) * 1000:.2f} ms')
            print(f'actual sample rate: {actual_sample_rate:.3f} Hz')
            print(f'average sample rate: {average_sample_rate:.3f} Hz')
            print()

            pred = self.model.predict(data)
            for p in pred:
                self.pred_buffer[i] = p
            i = (i + 1) % pred_buf_len


def load_model(e, d, c) -> RandomForestClassifier:
    model_path = config.model_save_dir_path / f'{e}_estimators_{d}_depth_{c}.model'
    with model_path.open('rb') as f:
        return pickle.load(f)
