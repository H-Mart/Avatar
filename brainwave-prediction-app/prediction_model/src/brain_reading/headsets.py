from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from threading import Event, Thread

from ..data_processing import config
from collections import Counter
import time
import numpy as np
import pandas as pd
import socket
import struct
from pathlib import Path
from os import environ

RELEVANT_COLS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30)

start_time = time.time()


def delta():
    return time.time() - start_time


environ['BRAINFLOW_BATCH_SIZE'] = str(config.brainflow_batch_size)


class HeadsetStreamer:
    def __init__(self, ip: str, port: int, board: BoardShim, buffer_size=2500):
        self.ip = ip
        self.port = port
        self.board = board
        self.buffer_size = buffer_size
        self.e = Event()

    def wait(self):
        time.sleep(.1)

    def start_stream(self, event: Event = None):
        # blocks thread until event is set
        # todo if event was passed in, only another thread can set it, since this is a blocking call
        if event is None:
            event = self.e
        with self:
            while not event.is_set():
                self.wait()

    def __enter__(self):
        self.board.prepare_session()
        self.board.start_stream(self.buffer_size, f"streaming_board://{self.ip}:{self.port}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.board.stop_stream()
        self.board.release_session()

    def get_listening_socket(self) -> socket.socket:
        return get_listening_socket(self.ip, self.port)


class PhysicalHeadsetStreamer(HeadsetStreamer):
    def __init__(self, ip, port, params: BrainFlowInputParams = BrainFlowInputParams(), buffer_size=2500):
        board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)
        super().__init__(ip, port, board, buffer_size)


class SyntheticHeadsetStreamer(HeadsetStreamer):
    def __init__(self, ip, port, params: BrainFlowInputParams = BrainFlowInputParams(), buffer_size=2500):
        board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
        super().__init__(ip, port, board, buffer_size)


class PlaybackHeadsetStreamer(HeadsetStreamer):
    def __init__(self, csv_file: str, master_board: BoardIds, ip, port,
                 params: BrainFlowInputParams = BrainFlowInputParams(),
                 buffer_size=2500):
        params.file = csv_file
        params.master_board = master_board
        board = BoardShim(BoardIds.PLAYBACK_FILE_BOARD.value, params)
        super().__init__(ip, port, board, buffer_size)


class SimHeadsetStreamer(HeadsetStreamer):
    class FileSim:
        def __init__(self, sample_rate, ip, port, behavior='random'):
            self.files = np.array(sorted([(p.relative_to(config.set_aside_path).parents[-2].name, p)
                                          for p in
                                          config.set_aside_path.glob('**/*.csv')]))

            self.df = None
            self.data_array = None
            self.sample_rate = sample_rate
            self.time_between_samples = 1 / sample_rate
            self.ip = ip
            self.port = port
            self.stream_thread = None
            self.sock = None
            self.behavior = behavior
            self.streaming = Event()
            self.package_buffer = np.empty(32 * config.brainflow_batch_size, dtype=np.float64)
            self.is_ready = False

        def interleave_files(self, n):
            category_counts = list(Counter([label for file, label in self.files]).values())
            category_indices = np.cumsum([0] + category_counts[:-1])
            interleaved = np.zeros(len(self.files), dtype=np.object_)
            while more := True:
                for i in range(len(category_counts)):
                    f_idx = category_indices[i]

        def prepare_session(self):
            self.df = self._load_files()
            self.data_array = self.df.drop(columns=self.df.columns[[-1, -2]]).to_numpy(copy=True, dtype=np.float64)

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            # self.sock.sendto(b'0', (self.ip, self.port))
            self.is_ready = True

        def start_stream(self, *args, **kwargs):
            def _stream():
                self._wait_for_ready()

                data_idx = buf_idx = 0
                last_file = self.df.iloc[buf_idx, -1]
                last_label = None

                while self.streaming.is_set():
                    if self.behavior == 'random':
                        data_idx = np.random.randint(0, len(self.data_array))
                    elif self.behavior == 'seq':
                        data_idx = (data_idx + 1) % len(self.data_array)

                    # if we switch files, send the buffer and reset the buffer index
                    file_being_indexed = self.df.iloc[data_idx, -1]
                    if last_file != file_being_indexed:
                        print(f'last file: {last_file}\nlast label: {last_label}')
                        print(f'current file: {file_being_indexed}\ncurrent label: {self.df.iloc[data_idx, -2]}')
                        last_file = file_being_indexed
                        last_label = self.df.iloc[data_idx, -2]
                        self.sock.sendto(self.package_buffer.tobytes(), (self.ip, self.port))
                        buf_idx = 0

                    # self.data_array[data_idx, 30] = time.time()
                    self.package_buffer[buf_idx:buf_idx + 32] = self.data_array[data_idx]
                    buf_idx += 32
                    if buf_idx == len(self.package_buffer):
                        buf_idx = 0
                        self.sock.sendto(self.package_buffer.tobytes(), (self.ip, self.port))

                    time.sleep(self.time_between_samples)

            self.streaming.set()
            self.stream_thread = Thread(target=_stream)
            self.stream_thread.start()

        def stop_stream(self):
            self.streaming.clear()
            self.stream_thread.join()

        def release_session(self):
            self.is_ready = False
            self.sock.close()
            self.df = None
            self.data_array = None

        def _wait_for_ready(self):
            while not self.is_ready:
                time.sleep(.1)

        def _load_files(self):
            dfs = []
            for file, label in self.files:
                df = pd.read_csv(file, index_col=None)
                df.drop(columns=df.columns[-1], inplace=True)  # drop the formatted timestamp column
                df['label'] = label
                df['file'] = file
                dfs.append(df)
            return pd.concat(dfs)

    def __init__(self, ip, port, sample_rate=250, behavior='random'):
        board = self.FileSim(sample_rate, ip, port, behavior)
        super().__init__(ip, port, board, 0)


def get_listening_socket(ip: str, port: int) -> socket.socket:
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow multiple sockets to use the same PORT number
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the server address
    sock.bind(('', port))
    sock.settimeout(5)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return sock


def main():
    sim = SimHeadsetStreamer(config.headset_streaming_host, config.headset_streaming_port, sample_rate=125,
                             behavior='seq')

    e = Event()
    sim.start_stream(e)
    time.sleep(600)
    e.set()


if __name__ == "__main__":
    # turn off warnings for testing
    import warnings

    warnings.warn = lambda *args, **kwargs: None

    main()
    # main()
