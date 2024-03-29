import PySimpleGUI as sg
import time
import cv2
from client.bci_connection import BCIConnection

from gui_windows.manual_drone_control_window import DroneControl
from gui_windows.brainwave_prediction_window import Brainwaves
from gui_windows.transfer_files_window import TransferData

from djitellopy import Tello

tello = Tello()


# receives action from a GUI button and executes a corresponding Tello-Drone class move action, then returns "Done"
def get_drone_action(action):
    translation_distance = 30
    rotation_angle = 45

    translation_actions = {
        'backward': tello.move_back,
        'down': tello.move_down,
        'forward': tello.move_forward,
        'left': tello.move_left,
        'right': tello.move_right,
        'up': tello.move_up,
    }

    rotation_actions = {
        'turn_left': tello.rotate_counter_clockwise,
        'turn_right': tello.rotate_clockwise,
    }

    other_actions = {
        'connect': tello.connect,
        'land': tello.land,
        'takeoff': tello.takeoff,
        'flip': tello.flip_back,
        'keep alive': tello.query_battery,
    }

    if action in translation_actions:
        translation_actions[action](translation_distance)
    elif action in rotation_actions:
        rotation_actions[action](rotation_angle)
    elif action in other_actions:
        other_actions[action]()
    elif action == 'stream':
        tello.streamon()
        frame_read = tello.get_frame_read()
        while True:
            print("truu")
            img = frame_read.frame
            cv2.imshow("drone", img)
    else:
        raise ValueError(f"Action {action} not recognized")

    return "Done"


def get_drone_action_testing(action):
    if action == 'connect':
        print("tello.connect()")
    elif action == 'backward':
        print('tello.move_back(30)')
    elif action == 'down':
        print('tello.move_down(30)')
    elif action == 'forward':
        print('tello.move_forward(30)')
    elif action == 'land':
        print('tello.land')
    elif action == 'left':
        print('tello.move_left(30)')
    elif action == 'right':
        print('tello.move_right(30)')
    elif action == 'takeoff':
        print('tello.takeoff')
    elif action == 'up':
        print('tello.move_up(30)')
    elif action == 'turn_left':
        print('tello.rotate_counter_clockwise(45)')
    elif action == 'turn_right':
        print('tello.rotate_clockwise(45)')
    elif action == 'flip':
        print("tello.flip('b')")
    elif action == 'keep alive':
        print("tello.query_battery()")
    elif action == 'stream':
        print("tello.streamon()")
    return "Done"


def drone_holding_pattern():
    print("Hold forward - tello.move(forward(5)")
    tello.move_forward(5)
    time.sleep(2)
    print("Hold backward - tello.move(backward(5)")
    tello.move_back(5)

    in_pattern = False
    # let calling Window know if it needs to restart Holding Pattern
    return in_pattern


def use_brainflow():
    bci = BCIConnection()
    server_response = bci.bci_connection_controller()
    return server_response


drone_action_func = get_drone_action_testing

brainwave_obj = Brainwaves(drone_action_func, use_brainflow)
brainwave_tab = brainwave_obj.get_window()

transfer_data_obj = TransferData()
transfer_data_tab = transfer_data_obj.get_window()

drone_control_obj = DroneControl(drone_action_func)
manual_drone_ctrl_tab = drone_control_obj.get_window()

layout = [[sg.TabGroup([[
    brainwave_tab,
    transfer_data_tab,
    manual_drone_ctrl_tab]],
    key='layout', enable_events=True)]]

# Create the windows
window = sg.Window('Start Page', layout, size=(800, 800), element_justification='c', resizable=True, finalize=True)

# Event loop for the first window
# changed what the buttons do to tabs
while True:
    event, values = window.read()
    activeTab = window['layout'].get()

    if event == sg.WIN_CLOSED:
        break

    elif activeTab == brainwave_obj.name:
        brainwave_obj.button_loop(window, event, values)
    elif activeTab == transfer_data_obj.name:
        transfer_data_obj.button_loop(window, event, values)
    elif activeTab == drone_control_obj.name:
        drone_control_obj.button_loop(window, event, values)

    window.refresh()
