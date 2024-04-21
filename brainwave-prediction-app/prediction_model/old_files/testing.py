from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from pathlib import Path
import time
import threading
import numpy as np
import pandas as pd
import socket
import struct
from ..data_processing import config
import pickle

np.set_printoptions(formatter={'float': '{: 0.4f}'.format})

start_time = time.time()
relevant_cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 30]

Event = threading.Event()


def load_model():
    model_path = config.model_save_dir_path / '200_estimators_32_depth_gini.model'
    with model_path.open('rb') as f:
        return pickle.load(f)


def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn


def classify_data(data, model):
    # data = data[:, relevant_cols]
    # print(data[:, -1])
    return model.predict(data)


def delta():
    return time.time() - start_time


def delta2(t):
    return time.time() - t


def read_server():
    # Multicast IP and port BrainFlow is sending data to
    multicast_group = '224.0.0.1'
    multicast_port = 5006

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow multiple sockets to use the same PORT number
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the server address
    sock.bind(('', multicast_port))
    sock.settimeout(1)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    model = load_model()
    model.verbose = 0

    # Receive/respond loop
    print('Waiting to receive multicast message...')
    buf = np.empty(32 * 8, dtype=np.float64)

    label_map = {0: 'forward', 1: 'land', 2: 'takeoff', 3: 'backward', 4: 'left', 5: 'right'}

    i = 0
    # data = np.empty((2000, 21), dtype=np.float64)
    ratios = np.zeros(6)
    while not Event.is_set():
        try:
            nbytes, address = sock.recvfrom_into(buf)
        except socket.timeout:
            continue
        num_rows = nbytes // 256
        pred = classify_data(buf[:nbytes // 8].reshape(num_rows, 32)[:, relevant_cols], model)
        ratios += np.bincount(pred, minlength=6)
        i += num_rows
    print(ratios)
    ratios /= i
    for k, v in label_map.items():
        print(f'{v}: {ratios[k]}')
        print()


def stream_to_file():
    params = BrainFlowInputParams()
    board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
    print(
        f'BoardShim object created: {board}, type: {type(board)}, sample rate: {board.get_sampling_rate(board.get_board_id())}')
    board.prepare_session()
    board.start_stream(45000, "file://eeg_data.csv:w")
    print('start sleeping in the main thread')
    while delta() < 60:
        time.sleep(.1)
    board.stop_stream()
    board.release_session()


def stream_to_server():
    params = BrainFlowInputParams()
    board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
    board.prepare_session()
    board.start_stream(2500, "streaming_board://224.0.0.1:5006")
    # print('start sleeping in the main thread')
    while delta() < 15:
        time.sleep(.1)
    Event.set()
    board.stop_stream()
    board.release_session()


def predict(csv: Path):
    df = pd.read_csv(csv, index_col=None).sort_values(by=' Timestamp')
    df.drop(columns=df.columns[-1], inplace=True)
    f = (Path('./temp') / 'temp.csv')

    df.to_csv(f, index=False, header=False, mode='w')

    model = load_model()
    model.verbose = 0

    label_map = {0: 'forward', 1: 'land', 2: 'takeoff', 3: 'backward', 4: 'left', 5: 'right'}

    data = pd.read_csv(f, index_col=None, header=None).to_numpy()
    data = data[:, relevant_cols]
    data[:, -1] = 0
    pred = model.predict(data)
    ratios = np.bincount(pred, minlength=6) / len(pred)
    print(ratios)
    for k, v in label_map.items():
        print(f'{v}: {ratios[k]}')
        print()


def stream_playback_to_server():
    params = BrainFlowInputParams()

    temp_dir = Path('./temp')
    temp_dir.mkdir(exist_ok=True)

    from random import choice
    category = choice(list((config.processed_dir_path).iterdir()))
    true_label = category.name
    csv = choice(list(category.iterdir()))

    df = pd.read_csv(csv, index_col=None)
    df.drop(columns=df.columns[-1], inplace=True)
    f = (temp_dir / 'temp.csv')

    df.to_csv(f, index=False, header=False, mode='w')

    params.file = str(f)

    params.master_board = BoardIds.CYTON_DAISY_BOARD
    board = BoardShim(BoardIds.PLAYBACK_FILE_BOARD.value, params)
    board.prepare_session()
    board.start_stream(2500, "streaming_board://224.0.0.1:5006")
    # print('start sleeping in the main thread')
    while delta() < 15:
        time.sleep(1 / 250)

    Event.set()
    board.stop_stream()
    board.release_session()

    print(f'true_label: {true_label}')
    print(f'csv: {csv}')

    for file in temp_dir.iterdir():
        file.unlink()

    temp_dir.rmdir()


def main():
    t1 = threading.Thread(target=stream_playback_to_server)
    t2 = threading.Thread(target=read_server)
    t1.start()
    t2.start()
    t1.join()
    print('t1 joined')
    t2.join()
    print('t2 joined')


if __name__ == "__main__":


    # temp_dir = Path('./temp')
    # temp_dir.mkdir(exist_ok=True)
    #
    # from random import choice
    #
    # category = choice(list((config.processed_dir_path).iterdir()))
    # true_label = category.name
    # csv = choice(list(category.iterdir()))
    #
    # predict(csv)
    #
    # print(f'true_label: {true_label}')
    # print(f'csv: {csv}')
    #
    # for file in temp_dir.iterdir():
    #     file.unlink()
    #
    # temp_dir.rmdir()
