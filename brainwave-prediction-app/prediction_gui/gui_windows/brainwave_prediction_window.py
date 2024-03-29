import PySimpleGUI as sg

from .bci_gui_tab import BCIGuiTab

from ..client.drone import get_drone_action_testing, execute_drone_action
from ..client.bci_connection import BCIConnection


# changed script design to class object for variable retention in tabs
class BrainwaveTab(BCIGuiTab):
    def __init__(self, name: str = 'Brainwave Reading'):
        self.name = name

        self.bci_connection = BCIConnection()

        self.flight_log = []  # array to hold flight log info
        self.predictions_log = []  # array to hold info for table

        self.predictions_headings = ['Predictions Count', 'Server Predictions', 'Prediction Label']
        self.response_headings = ['Count', 'Label']

        self.count = 0
        self.prediction_label = None

        self.read_my_mind_button = sg.Button('Read my mind...', size=(40, 5),
                                             image_filename="images/brain.png", key=self.key('read_mind'))
        self.not_what_i_was_thinking_button = sg.Button('Not what I was thinking...', size=(14, 3),
                                                        key=self.key('not_thinking'))
        self.execute_button = sg.Button('Execute', size=(14, 3), key=self.key('execute'))
        self.connect_button = sg.Button('Connect', size=(8, 2), image_filename="images/connect.png",
                                        key=self.key('connect'))
        self.keep_alive_button = sg.Button('Keep Drone Alive', key=self.key('keep_alive'))

    @property
    def tab_name(self) -> str:
        return self.name

    # changed the method to return a tab for the tabgroup
    def get_tab(self):
        top_left = [
            [sg.Radio('Manual Control', 'pilot', default=True, size=(-20, 1)),
             sg.Radio('Autopilot', 'pilot', size=(12, 1))],
            [self.read_my_mind_button],
            [sg.Text("The model says ...")],
            [sg.Table(values=[], headings=self.response_headings, auto_size_columns=False, def_col_width=15,
                      justification='center',
                      num_rows=1, key=self.key('-SERVER_TABLE-'), row_height=25, tooltip="Server Response Table",
                      hide_vertical_scroll=True)],
            [self.not_what_i_was_thinking_button,
             self.execute_button, sg.Push()],
            [sg.Input(key=self.key('-drone_input-')),
             self.keep_alive_button]
        ]

        bottom_left = [
            [sg.Text('Flight Log')],
            [sg.Listbox(values=self.flight_log, size=(30, 6), key=self.key('LOG'))],
        ]

        bottom_right = [
            [sg.Text('Console Log')],
            [sg.Output(s=(45, 10))]
        ]

        brainwave_prediction_layout = [
            [sg.Column(top_left, pad=((150, 0), (0, 0))), sg.Push(), sg.Table(
                values=[],
                headings=self.predictions_headings,
                max_col_width=35,
                auto_size_columns=True,
                justification='center',
                num_rows=10,
                key=self.key('-TABLE-'),
                row_height=35,
                tooltip='Predictions Table'
            )
             ],

            [sg.Column(bottom_left), sg.Push(),
             sg.Column(bottom_right)],

            [self.connect_button,
             sg.Push()],
        ]

        tab = sg.Tab(self.name, brainwave_prediction_layout, key=self.name)
        return tab

    def set_server_table(self, window, count, prediction_label):
        server_record = [[count, prediction_label]]
        window[self.key('-SERVER_TABLE-')].update(values=server_record)

    def add_to_flight_log(self, window, text):
        self.flight_log.insert(0, text)
        window[self.key('LOG')].update(values=self.flight_log)

    def add_to_predictions_log(self, window, prediction_count, server_predictions, prediction_label):
        prediction_record = [prediction_count, server_predictions, prediction_label]
        self.predictions_log.append(prediction_record)
        window[self.key('-TABLE-')].update(values=self.predictions_log)

    def handle_event(self, window, event, values):
        prediction_label = None

        if event == self.read_my_mind_button.key:
            prediction_response = self.bci_connection.read_and_transmit_data_from_board()
            self.count = prediction_response['prediction_count']
            prediction_label = prediction_response['prediction_label']
            self.set_server_table(window, self.count, prediction_label)

        elif event == self.not_what_i_was_thinking_button.key:
            get_drone_action_testing(values['-drone_input-'])
            self.add_to_predictions_log(window, "manual", "predict",
                                        f"{values['-drone_input-']}")

        elif event == self.execute_button.key:
            self.add_to_flight_log(window, prediction_label)
            get_drone_action_testing(prediction_label)
            self.add_to_flight_log(window, "done")
            self.add_to_predictions_log(window, len(self.predictions_log) + 1, self.count, prediction_label)

        elif event == self.connect_button.key:
            self.add_to_flight_log(window, "Connect button pressed")
            get_drone_action_testing('connect')
            self.add_to_flight_log(window, "Done.")

        elif event == self.keep_alive_button.key:
            get_drone_action_testing('keep alive')
