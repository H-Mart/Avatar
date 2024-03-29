import numpy as np

from .headsets import get_listening_socket
from ..data_processing import config

from threading import Thread, Event

HEADSET_DATA_LENGTH_BYTES = 256
HEADSET_DATA_LENGTH_FLOATS = 32

RELEVANT_COLS = np.arange(32)

columns = ['Sample Index', ' EXG Channel 0', ' EXG Channel 1', ' EXG Channel 2',
           ' EXG Channel 3', ' EXG Channel 4', ' EXG Channel 5', ' EXG Channel 6',
           ' EXG Channel 7', ' EXG Channel 8', ' EXG Channel 9', ' EXG Channel 10',
           ' EXG Channel 11', ' EXG Channel 12', ' EXG Channel 13',
           ' EXG Channel 14', ' EXG Channel 15', ' Accel Channel 0',
           ' Accel Channel 1', ' Accel Channel 2', ' Other', ' Other.1',
           ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
           ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2',
           ' Timestamp', ' Other.7']


class Receiver:
    def __init__(self, sampling_rate, period=1):
        self.sock = get_listening_socket(config.headset_streaming_host, config.headset_streaming_port)
        self.sock.setblocking(0)

        self.sample_buffer = np.empty(32 * config.brainflow_batch_size, dtype=np.float64)

        self.stop_event = Event()

    def __enter__(self):
        self.stop_event.clear()
        gen = self.generator()
        next(gen)
        return gen

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()

    def stop(self):
        self.stop_event.set()

    def generator(self):
        while not self.stop_event.is_set():
            new_data = None
            while True:
                try:
                    nbytes, _ = self.sock.recvfrom_into(self.sample_buffer)
                    new_data = True
                except BlockingIOError:
                    break
            if new_data:
                num_rows = nbytes // HEADSET_DATA_LENGTH_BYTES
                data = (self.sample_buffer[:num_rows * HEADSET_DATA_LENGTH_FLOATS]
                        .reshape((num_rows, HEADSET_DATA_LENGTH_FLOATS))[:, RELEVANT_COLS])
                yield data
