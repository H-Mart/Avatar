from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from threading import Event, Thread

from ..data_processing import config

import time
import numpy as np
import socket
import struct

start_time = time.time()


def delta():
    return time.time() - start_time


class HeadsetStreamer:
    def __init__(self, ip: str, port: int, board: BoardShim, buffer_size=2500):
        self.ip = ip
        self.port = port
        self.board = board
        self.buffer_size = buffer_size

    def stream_blocking(self):
        time.sleep(.1)

    def stream_threaded(self, event: Event):
        def _stream():
            with self as s:
                while not event.is_set():
                    s.stream_blocking()

        t = Thread(target=_stream)
        t.start()
        return t

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


class SimHeadsetStreamer(HeadsetStreamer):
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


def get_listening_socket(ip: str, port: int) -> socket.socket:
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow multiple sockets to use the same PORT number
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the server address
    sock.bind(('', port))
    sock.settimeout(1)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return sock


def main():
    streamer = SimHeadsetStreamer(config.headset_streaming_host, config.headset_streaming_port)
    e = Event()
    s_t = streamer.stream_threaded(e)

    time.sleep(60)

    e.set()
    s_t.join()


if __name__ == "__main__":
    main()
