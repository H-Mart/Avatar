from abc import ABC, abstractmethod, abstractproperty
from PySimpleGUI import Window, Tab


class BCIGuiTab(ABC):

    @abstractmethod
    def __init__(self, *args, name: str, **kwargs):
        pass

    @abstractmethod
    def get_window(self) -> Tab:
        pass

    @abstractmethod
    def button_loop(self, window: Window, event, values):
        pass

    @property
    @abstractmethod
    def tab_name(self) -> str:
        """Returns the name of the tab"""
        return ''

    def key(self, key: str) -> str:
        """
        Returns the key with the tab name prepended to it so that it is unique to the tab,
        useful since the keys are unique to the window, not the tab
        """
        return f'{self.tab_name} - {key}'
