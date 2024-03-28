import time
import numpy as np
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds


class BCIConnection:

    def __init__(self):
        self.column_labels = None

    def read_from_board(self):

        # use synthetic board for demo
        # params = BrainFlowInputParams()
        # params.serial_port = "/dev/cu.usbserial-D200PMA1"
        # board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)

        params = BrainFlowInputParams()
        board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)

        board.prepare_session()
        board.start_stream(streamer_params="streaming_board://225.1.1.1:6677")
        BoardShim.log_message(LogLevels.LEVEL_INFO,
                              'start sleeping in the main thread')
        time.sleep(10)
        data = board.get_board_data()
        board.stop_stream()
        board.release_session()
        return data

    def send_data_to_server(self, data):
        print('Transposed Data From the Board')
        df = pd.DataFrame(np.transpose(data), columns=self.column_labels)

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

            # format data cols.
            self.column_labels = []
            for num in range(32):
                self.column_labels.append("c" + str(num))

            # read eeg data from the board -- will start a bci session with your current board
            # allowing it to stream to BCI Gui App and collect 10 second data sample
            data = self.read_from_board()
            # Sends preprocessed data via http request to get a prediction
            server_response = self.send_data_to_server(data)
            server_response.raise_for_status()
            return server_response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Status Code: {http_err.response.status_code}')
        except Exception as e:
            print("Non-http error occurred during EEG data collection or transmission")
            print(e)
