import PySimpleGUI as sg
from .bci_gui_tab import BCIGuiTab
from dataclasses import dataclass


# changes method layout to class design for retention of data
class DroneControl(BCIGuiTab):
    def __init__(self, get_drone_action, name='Manual Drone Control'):
        self.log_items = []
        self.first_iteration = True
        self.get_drone_action = get_drone_action
        self.name = name

    @property
    def tab_name(self) -> str:
        return self.name

    def add_item_to_log(self, item, window=None):
        self.log_items.insert(0, item)
        if window:
            log = window[self.key('LOG')]
            window[self.key('LOG')].update(values=self.log_items)
            window.refresh()

    # sets the layout and returns a tab for the tabgroup
    def get_window(self):
        # Define the layout for the Manual Drone Control Page
        # NEW CHANGES: Added expand_x and expand_y parameters so elements scale with the window, should scale, but buttons are misaligned.
        top_center = [
            [sg.Button('Up', size=(8, 2), expand_x=True, expand_y=True, image_filename="images/up.png")]]
        top_right = [[sg.Text('Flight Log')], [sg.Listbox(
            values=[], size=(40, 5), key=self.key('LOG'))]]
        bottom_center = [
            [sg.Button('Down', size=(8, 2), expand_x=True, expand_y=True, image_filename="images/down.png")]]

        manual_drone_control_layout = [
            [sg.Button('Home', size=(8, 2), image_filename="images/home.png"),
             sg.Column(top_center, expand_x=True, expand_y=True, pad=((0, 0), (0, 0))), sg.Column(top_right)],

            [sg.Button('Forward', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename="images/forward.png")],

            [sg.Button('Turn Left', size=(8, 2), expand_x=True, expand_y=True, image_filename="images/turnLeft.png"),
             sg.Button('Left', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename="images/left.png"),
             sg.Button('Stream', expand_x=True, expand_y=True, image_filename="images/drone.png"),
             sg.Button('Right', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename="images/right.png"),
             sg.Button('Turn Right', size=(8, 2), expand_x=True, expand_y=True, image_filename="images/turnRight.png")],

            [sg.Button('Back', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename="images/back.png")],

            [sg.Button('Connect1', size=(8, 2), image_filename="images/connect.png"),
             sg.Column(bottom_center, expand_x=True, expand_y=True, pad=((0, 0), (0, 0))),
             sg.Button('Takeoff', size=(8, 2), image_filename="images/takeoff.png"),
             sg.Button('Land', size=(8, 2), image_filename="images/land.png")]]

        tab = sg.Tab(self.name, manual_drone_control_layout, key=self.name)
        return tab

    def button_loop(self, window, event, values):
        if self.first_iteration:
            self.add_item_to_log("---------- NEW LOG ----------", window=window)
            self.first_iteration = False

        if event == 'Up':
            self.get_drone_action('up')
            self.add_item_to_log("Up button pressed", window=window)
            self.add_item_to_log('done', window=window)
        elif event == 'Down':
            self.add_item_to_log("Down button pressed", window=window)
            self.get_drone_action('down')
            self.add_item_to_log('done', window=window)
        elif event == 'Forward':
            self.add_item_to_log("Forward button pressed", window=window)
            self.get_drone_action('forward')
            self.add_item_to_log('done', window=window)
        elif event == 'Back':
            self.add_item_to_log("Back button pressed", window=window)
            self.get_drone_action('backward')
            self.add_item_to_log('done', window=window)
        elif event == 'Left':
            self.add_item_to_log("Left button pressed", window=window)
            self.get_drone_action('left')
            self.add_item_to_log('done', window=window)
        elif event == 'Right':
            self.add_item_to_log("Right button pressed", window=window)
            self.get_drone_action('right')
            self.add_item_to_log('done', window=window)
        elif event == 'Turn Left':
            self.add_item_to_log("Turn Left button pressed", window=window)
            self.get_drone_action('turn_left')
            self.add_item_to_log('done', window=window)
        elif event == 'Turn Right':
            self.add_item_to_log("Turn right button pressed", window=window)
            self.get_drone_action('turn_right')
            self.add_item_to_log('done', window=window)
        elif event == 'Takeoff':
            self.add_item_to_log("Takeoff button pressed", window=window)
            self.get_drone_action('takeoff')
            self.add_item_to_log("Done.", window=window)
        elif event == 'Land':
            self.add_item_to_log("Land button pressed", window=window)
            self.get_drone_action('land')
            self.add_item_to_log('done', window=window)
        elif event == 'Home':
            self.first_iteration = True
        elif event == 'Connect1':
            self.add_item_to_log("Connect button pressed", window=window)
            self.get_drone_action('connect')
            self.add_item_to_log("Done.", window=window)
        elif event == 'Stream':
            self.get_drone_action('stream')
