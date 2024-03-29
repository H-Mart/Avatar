import PySimpleGUI as sg
import sys
from .signal_module import signalling_system as sgsys
from .bci_gui_tab import BCIGuiTab
from typing import Callable


# changed script design to class object for variable retention in tabs
class Brainwaves(BCIGuiTab):
    def __init__(self, get_drone_action: Callable, use_brainflow: Callable, name: str = 'Brainwave Reading'):
        self.signal_system = sgsys(get_drone_action, "holding pattern")  # The signal system class

        self.keep_alive_toggle = False  # mimics the drone's keep alive toggle

        self.flight_log = []  # array to hold flight log info
        self.predictions_log = []  # array to hold info for table
        self.predictions_headings = [
            'Predictions Count', 'Server Predictions', 'Prediction Label']  # table headings
        self.response_headings = ['Count', 'Label']
        self.count = 0
        self.predictions_list = ['backward', 'down', 'forward',
                                 'land', 'left', 'right', 'takeoff', 'up']
        self.action_index = 0

        self.use_brainflow = use_brainflow
        self.get_drone_action = get_drone_action
        self.name = name

    @property
    def tab_name(self) -> str:
        return "Brainwave Reading"

    # changed the method to return a tab for the tabgroup
    def get_window(self):
        top_left = [
            [sg.Radio('Manual Control', 'pilot', default=True, size=(-20, 1)),
             sg.Radio('Autopilot', 'pilot', size=(12, 1))],
            [sg.Button('Read my mind...', size=(40, 5),
                       image_filename="images/brain.png")],
            [sg.Text("The model says ...")],
            [sg.Table(values=[], headings=self.response_headings, auto_size_columns=False, def_col_width=15,
                      justification='center',
                      num_rows=1, key=self.key('-SERVER_TABLE-'), row_height=25, tooltip="Server Response Table",
                      hide_vertical_scroll=True, )],

            [sg.Button('Not what I was thinking...', size=(14, 3)),
             sg.Button('Execute', size=(14, 3)), sg.Push()],
            [sg.Input(key=self.key('-drone_input-')),
             sg.Button('Keep Drone Alive')]
        ]

        bottom_left = [
            [sg.Text('Flight Log')], [sg.Listbox(
                values=self.flight_log, size=(30, 6), key=self.key('LOG'))],
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

            [sg.Button('Connect', size=(8, 2), image_filename="images/connect.png"),
             sg.Push()],
        ]

        tab = sg.Tab(self.name, brainwave_prediction_layout, key=self.name)
        return tab

    # loops through for reading which button is pressed when this tab is open
    def button_loop(self, window, event, values):
        prediction_label = None

        if event == "Read my mind...":
            prediction_response = self.use_brainflow()
            self.count = prediction_response['prediction_count']
            prediction_label = prediction_response['prediction_label']
            server_record = [[self.count, prediction_label]]
            window[self.key('-SERVER_TABLE-')].update(
                values=server_record)
        elif event == "Not what I was thinking...":
            self.get_drone_action(values['-drone_input-'])
            prediction_record = ["manual", "predict", f"{values['-drone_input-']}"]
            self.predictions_log.append(prediction_record)
            window[self.key('-TABLE-')].update(values=self.predictions_log)
        elif event == "Execute":
            self.flight_log.insert(0, prediction_label)
            window[self.key('LOG')].update(values=self.flight_log)
            self.get_drone_action(prediction_label)
            print("done")
            self.flight_log.insert(0, "done")
            window[self.key('LOG')].update(values=self.flight_log)
            prediction_record = [
                len(self.predictions_log) + 1, self.count, prediction_label]
            self.predictions_log.append(prediction_record)
            window[self.key('-TABLE-')].update(
                values=self.predictions_log)
        elif event == 'Connect':
            self.flight_log.insert(0, "Connect button pressed")
            window[self.key('LOG')].update(values=self.flight_log)
            self.get_drone_action('connect')
            self.flight_log.insert(0, "Done.")
            window[self.key('LOG')].update(values=self.flight_log)
        elif event == 'Keep Drone Alive':
            self.get_drone_action('keep alive')
