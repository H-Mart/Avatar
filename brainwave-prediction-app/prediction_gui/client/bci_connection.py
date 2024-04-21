import pathlib
import time
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
import os


class BCIConnection:
    def __init__(self, prediction_server_url: str = 'http://localhost:5000', serial_port: str = '/dev/ttyUSB0',
                 use_fake_bci: bool = True):
        self.board = None
        self._synthetic_board = None
        self._cyton_daisy_board = None
        self._file_playback_board = None

        if os.environ.get('BCI_GUI_SERIAL_PORT'):
            serial_port = os.environ['BCI_GUI_SERIAL_PORT']
            print(f'Using serial port from environment variable: {serial_port}')
        else:
            print(f'Using default serial port: {serial_port}')
        self.serial_port = serial_port

        if os.environ.get('BCI_GUI_PREDICTION_SERVER_URL'):
            prediction_server_url = os.environ['BCI_GUI_PREDICTION_SERVER_URL']
            print(f'Using prediction server URL from environment variable: {prediction_server_url}')
        else:
            print(f'Using default prediction server URL: {prediction_server_url}')
        self.prediction_server_url = prediction_server_url

        self._synthetic_board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, BrainFlowInputParams())

        cyton_daisy_params = BrainFlowInputParams()
        cyton_daisy_params.serial_port = self.serial_port
        self._cyton_daisy_board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, cyton_daisy_params)

    def load_file_board(self, file_path: pathlib.Path):
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')
        params = BrainFlowInputParams()
        params.file = str(file_path)
        params.master_board = BoardIds.CYTON_DAISY_BOARD
        self.board = BoardShim(BoardIds.PLAYBACK_FILE_BOARD.value, params)

    def load_synthetic_board(self):
        if self._synthetic_board is None:
            raise ValueError('Synthetic board must be initialized before loading synthetic board')
        self.board = self._synthetic_board

    def load_cyton_daisy_board(self):
        if self._cyton_daisy_board is None:
            raise ValueError('Cyton Daisy board must be initialized before loading Cyton Daisy board')
        self.board = self._cyton_daisy_board

    def _read_from_board(self):
        """
        This function will start a bci session with the board and collect 10 seconds of data
        Returns: a 2D numpy array of the data collected

        """
        self.board.prepare_session()
        self.board.start_stream()
        BoardShim.log_message(LogLevels.LEVEL_INFO, 'start sleeping in the main thread')

        time.sleep(10)
        data = self.board.get_board_data()
        self.board.stop_stream()
        self.board.release_session()
        return data

    def _send_data_to_server(self, data):
        """
        This function will send the data to the prediction server in the same format that the board outputs
        Returns: the response object from the server
        """
        df = pd.DataFrame(data)
        data_json = df.to_json()

        prediction_endpoint_url = f'{self.prediction_server_url}/eegrandomforestprediction'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(prediction_endpoint_url, data=data_json, headers=headers)
        return response

    def read_and_transmit_data_from_board(self):
        """
        Collects a 10 second sample of EEG data from the board and sends it to the prediction server for labeling
        Returns: the response from the server
        """
        error = ''
        try:
            BoardShim.enable_dev_board_logger()
            data = self._read_from_board()
            server_response = self._send_data_to_server(data)
            server_response.raise_for_status()

            server_json = server_response.json()

            print(f'Received response from server: {server_json}')

            if 'error' in server_json:
                error = server_json['error']
                return {'error': error}
            else:
                return {
                    'prediction_label': server_json['prediction_label'],
                    'prediction_count': server_json['prediction_count']
                }
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Status Code: {http_err.response.status_code}')
            error = f'Status Code: {http_err.response.status_code}'
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Connection error occurred: {conn_err}')
            error = conn_err
        except requests.exceptions.Timeout as timeout_err:
            print(f'Timeout error occurred: {timeout_err}')
            error = timeout_err
        except requests.exceptions.RequestException as req_err:
            print(f'Request error occurred: {req_err}')
            error = req_err
        except Exception as e:
            print('Non-http error occurred during EEG data collection or transmission')
            print(e)
            error = e

        return {'error': str(error)}


if __name__ == '__main__':
    from pathlib import Path

    bci_connection = BCIConnection()
    bci_connection.load_file_board(
        Path(r'/mnt/c/Users/henry/Documents/School/csci 495/Avatar/brainwave-prediction-app/files_for_synthetic_run/left.txt'))
    resp = bci_connection.read_and_transmit_data_from_board()
    print(resp)
