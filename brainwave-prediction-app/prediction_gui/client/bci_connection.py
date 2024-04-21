import time
import pandas as pd
import requests
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
import os


class BCIConnection:
    def __init__(self, prediction_server_url: str = 'http://localhost:5000', serial_port: str = '/dev/ttyUSB0',
                 use_fake_bci: bool = True):

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

        if os.environ.get('BCI_GUI_USE_FAKE_BCI'):
            use_fake_bci = False # todo change to True
            print('Using fake BCI from environment variable')
        else:
            print(f'Using default fake BCI setting: {use_fake_bci}')

        if use_fake_bci:
            print('Using synthetic board')
            self.board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, BrainFlowInputParams())
        else:
            print(f'Using Cyton Daisy board with serial port: {self.serial_port}')
            params = BrainFlowInputParams()
            params.serial_port = self.serial_port
            self.board = BoardShim(BoardIds.CYTON_DAISY_BOARD.value, params)

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
