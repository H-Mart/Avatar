import PySimpleGUI as sg
from .bci_gui_tab import BCIGuiTab
from pathlib import Path
from dataclasses import dataclass

from ..client.drone import Drone


# changes method layout to class design for retention of data
class DroneControlTab(BCIGuiTab):
    def __init__(self, drone: Drone, name='Manual Drone Control', image_dir: str = 'images'):
        self.log_items = []
        self.drone = drone
        self.name = name
        self.image_dir = image_dir

    @property
    def tab_name(self) -> str:
        return self.name

    def add_item_to_log(self, item, window=None):
        self.log_items.append(item)
        if window:
            log = window[self.key('LOG')]
            window[self.key('LOG')].update(value='\n'.join(self.log_items))
            window.refresh()

    def get_tab(self):
        # Define the layout for the Manual Drone Control Page
        # NEW CHANGES: Added expand_x and expand_y parameters so elements scale with the window,
        # should scale, but buttons are misaligned.

        top_center = [
            [sg.Button('Up', size=(8, 2), expand_x=True, expand_y=True, image_filename=f'{self.image_dir}/up.png')]]
        top_right = [[sg.Text('Flight Log')],
                     [sg.Multiline(default_text='---------- NEW LOG ----------', auto_refresh=True,
                                   autoscroll=True, write_only=True, size=(40, 5), key=self.key('LOG'))]]
        bottom_center = [
            [sg.Button('Down', size=(8, 2), expand_x=True, expand_y=True, image_filename=f'{self.image_dir}/down.png')]]

        manual_drone_control_layout = [
            [sg.Button('Home', size=(8, 2), image_filename=f'{self.image_dir}/home.png'),
             sg.Column(top_center, expand_x=True, expand_y=True, pad=((0, 0), (0, 0))), sg.Column(top_right)],

            [sg.Button('Forward', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/forward.png')],

            [sg.Button('Turn Left', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/turnLeft.png'),
             sg.Button('Left', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/left.png'),
             sg.Button('Stream', expand_x=True, expand_y=True, image_filename=f'{self.image_dir}/drone.png'),
             sg.Button('Right', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/right.png'),
             sg.Button('Turn Right', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/turnRight.png')],

            [sg.Button('Back', size=(8, 2), expand_x=True, expand_y=True,
                       image_filename=f'{self.image_dir}/back.png')],

            [sg.Button('Connect1', size=(8, 2), image_filename=f'{self.image_dir}/connect.png'),
             sg.Column(bottom_center, expand_x=True, expand_y=True, pad=((0, 0), (0, 0))),
             sg.Button('Takeoff', size=(8, 2), image_filename=f'{self.image_dir}/takeoff.png'),
             sg.Button('Land', size=(8, 2), image_filename=f'{self.image_dir}/land.png')]]

        tab = sg.Tab(self.name, manual_drone_control_layout, key=self.name)
        return tab

    def handle_event(self, window, event, values):
        if event == 'Up':
            self.drone.send_action('up')
            self.add_item_to_log('Up button pressed', window=window)
            self.add_item_to_log('done', window=window)
        elif event == 'Down':
            self.add_item_to_log('Down button pressed', window=window)
            self.drone.send_action('down')
            self.add_item_to_log('done', window=window)
        elif event == 'Forward':
            self.add_item_to_log('Forward button pressed', window=window)
            self.drone.send_action('forward')
            self.add_item_to_log('done', window=window)
        elif event == 'Back':
            self.add_item_to_log('Back button pressed', window=window)
            self.drone.send_action('backward')
            self.add_item_to_log('done', window=window)
        elif event == 'Left':
            self.add_item_to_log('Left button pressed', window=window)
            self.drone.send_action('left')
            self.add_item_to_log('done', window=window)
        elif event == 'Right':
            self.add_item_to_log('Right button pressed', window=window)
            self.drone.send_action('right')
            self.add_item_to_log('done', window=window)
        elif event == 'Turn Left':
            self.add_item_to_log('Turn Left button pressed', window=window)
            self.drone.send_action('turn_left')
            self.add_item_to_log('done', window=window)
        elif event == 'Turn Right':
            self.add_item_to_log('Turn right button pressed', window=window)
            self.drone.send_action('turn_right')
            self.add_item_to_log('done', window=window)
        elif event == 'Takeoff':
            self.add_item_to_log('Takeoff button pressed', window=window)
            self.drone.send_action('takeoff')
            self.add_item_to_log('Done.', window=window)
        elif event == 'Land':
            self.add_item_to_log('Land button pressed', window=window)
            self.drone.send_action('land')
            self.add_item_to_log('done', window=window)
        elif event == 'Home':
            print('no')
        elif event == 'Connect1':
            self.add_item_to_log('Connect button pressed', window=window)
            self.drone.send_action('connect')
            self.add_item_to_log('Done.', window=window)
        elif event == 'Stream':
            print('no')
