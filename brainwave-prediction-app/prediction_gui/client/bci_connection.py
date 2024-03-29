import time
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds


class BCIConnection:
    def __init__(self, headset_ip: str = '225.1.1.1', headset_port: int = 6677,
                 prediction_server_ip: str = '127.0.0.1', prediction_server_port: int = 5000):
        # params = BrainFlowInputParams()
        # params.serial_port = "/dev/cu.usbserial-D200PMA1"
        # board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)

        params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)

        self.headset_ip = headset_ip
        self.headset_port = headset_port

        self.prediction_server_ip = prediction_server_ip
        self.prediction_server_port = prediction_server_port

    def _read_from_board(self):
        """
        This function will start a bci session with the board and collect 10 seconds of data
        Returns: a 2D numpy array of the data collected

        """
        self.board.prepare_session()
        self.board.start_stream(streamer_params=f"streaming_board://{self.headset_ip}:{self.headset_port}")
        BoardShim.log_message(LogLevels.LEVEL_INFO, 'start sleeping in the main thread')

        time.sleep(10)
        data = self.board.get_board_data()
        self.board.stop_stream()
        self.board.release_session()
        return data

    def _send_data_to_server(self, data, preprocessor=None):
        """
        This function will send the data to the prediction server in the same format that the board outputs
        Returns: the response object from the server
        """
        # todo make this work with our model
        df = pd.DataFrame(data)
        data_json = df.to_json()

        prediction_endpoint_url = f'http://{self.prediction_server_ip}:{self.prediction_server_port}/eegrandomforestprediction'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(prediction_endpoint_url, data=data_json, headers=headers)
        return response

    def read_and_transmit_data_from_board(self):
        """
        Collects a 10 second sample of EEG data from the board and sends it to the prediction server for labeling
        Returns: the response from the server
        """
        try:
            BoardShim.enable_dev_board_logger()
            data = self._read_from_board()
            server_response = self._send_data_to_server(data)
            server_response.raise_for_status()
            return server_response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Status Code: {http_err.response.status_code}')
        except Exception as e:
            print("Non-http error occurred during EEG data collection or transmission")
            print(e)
