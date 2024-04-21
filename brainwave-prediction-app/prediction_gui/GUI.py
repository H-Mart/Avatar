import PySimpleGUI as sg

import os

from .gui_windows.manual_drone_control_window import DroneControlTab
from .gui_windows.brainwave_prediction_window import BrainwaveTab
from .gui_windows.transfer_files_window import TransferDataTab
from .gui_windows.bci_gui_tab import BCIGuiTab

from .client.drone import Drone
from .client.bci_connection import BCIConnection


def create_tabs() -> dict[str, BCIGuiTab]:
    drone = Drone(testing=False)
    bci_connection = BCIConnection(use_fake_bci=False)

    # the order of the tabs is the order they will appear in the GUI (left to right)
    image_dir = str(os.path.join(os.path.dirname(__file__), 'images'))
    tabs = [
        BrainwaveTab(drone, bci_connection, image_dir=image_dir),
        TransferDataTab(),
        DroneControlTab(drone, image_dir=image_dir)
    ]

    return {t.name: t for t in tabs}


def create_tabgroup_layout(tabs: dict[str, BCIGuiTab]) -> list[list[sg.Element]]:
    return [[sg.TabGroup([[
        tab.get_tab() for tab in tabs.values()
    ]], key='tabgroup', enable_events=True)]]


def create_window(tabs: dict[str, BCIGuiTab]) -> sg.Window:
    layout = create_tabgroup_layout(tabs)
    return sg.Window('Start Page', layout, size=(1000, 1000), element_justification='c',
                     resizable=True, finalize=True)


def run_gui():
    tabs = create_tabs()
    window = create_window(tabs)

    while True:
        try:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                break
            elif event == 'reading_done':
                continue

            active_tab = tabs[window['tabgroup'].get()]
            active_tab.handle_event(window, event, values)
        except Exception as e:
            sg.popup_error(f"An error occurred: {e}")


if __name__ == '__main__':
    run_gui()
