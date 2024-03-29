import time
import numpy as np
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds


class BCIConnection:
    def __init__(self, ip: str = '225.1.1.1', port: int = 6677):
        self.column_labels = None

        # params = BrainFlowInputParams()
        # params.serial_port = "/dev/cu.usbserial-D200PMA1"
        # board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)

        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)

        self.ip = ip
        self.port = port

    def read_from_board(self):
        self.board.prepare_session()
        self.board.start_stream(streamer_params=f"streaming_board://{self.ip}:{self.port}")
        BoardShim.log_message(LogLevels.LEVEL_INFO, 'start sleeping in the main thread')

        time.sleep(10)
        data = self.board.get_board_data()
        self.board.stop_stream()
        self.board.release_session()
        return data

    def send_data_to_server(self, data, preprocessor=None):
        # todo make this work with our model
        df = pd.DataFrame(data, columns=self.column_labels)
        data_json = df.to_json()

        # Define the API endpoint URL
        url = 'http://127.0.0.1:5000/eegrandomforestprediction'

        # Set the request headers
        headers = {'Content-Type': 'application/json'}

        # Send the POST request with the data in the request body
        response = requests.post(url, data=data_json, headers=headers)
        return response

    def bci_connection_controller(self):
        try:
            BoardShim.enable_dev_board_logger()

            # format data cols
            self.column_labels = []
            for num in range(32):
                self.column_labels.append("c" + str(num))

            # read eeg data from the board -- will start a bci session with your current board
            # allowing it to stream to BCI Gui App and collect 10 second data sample
            data = self.read_from_board()
            server_response = self.send_data_to_server(data)
            server_response.raise_for_status()
            return server_response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Status Code: {http_err.response.status_code}')
        except Exception as e:
            print("Non-http error occurred during EEG data collection or transmission")
            print(e)
