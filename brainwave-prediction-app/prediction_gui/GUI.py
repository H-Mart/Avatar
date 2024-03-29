import PySimpleGUI as sg

from gui_windows.manual_drone_control_window import DroneControlTab
from gui_windows.brainwave_prediction_window import BrainwaveTab
from gui_windows.transfer_files_window import TransferDataTab
from gui_windows.bci_gui_tab import BCIGuiTab


def create_tabs() -> dict[str, BCIGuiTab]:
    # the order of the tabs is the order they will appear in the GUI (left to right)
    tabs = [
        BrainwaveTab(drone_action_func, use_brainflow),
        TransferDataTab(),
        DroneControlTab(drone_action_func)
    ]

    return {t.name: t for t in tabs}


def create_tabgroup_layout(tabs: dict[str, BCIGuiTab]) -> list[list[sg.Element]]:
    return [[sg.TabGroup([[
        tab.get_tab() for tab in tabs.values()
    ]], key='tabgroup', enable_events=True)]]


def create_window(tabs: dict[str, BCIGuiTab]) -> sg.Window:
    layout = create_tabgroup_layout(tabs)
    return sg.Window('Start Page', layout, size=(800, 800), element_justification='c',
                     resizable=True, finalize=True)


def run_gui():
    tabs = create_tabs()
    window = create_window(tabs)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        active_tab = tabs[window['tabgroup'].get()]
        active_tab.handle_event(window, event, values)


if __name__ == '__main__':
    run_gui()
