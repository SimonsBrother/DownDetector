import dataclasses
import sys
from pathlib import Path
import os

import openpyxl.worksheet.worksheet as pyxl


# Returns the current directory, allowing for frozen state (i.e., compiled exe)
# NOT MY OWN WORK; SOURCE:
# https://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
def getPath():
    path = None
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        path = Path(os.path.dirname(sys.executable))
        # parent_path = path.parent.absolute()
    elif __file__:
        path = Path(os.path.dirname(__file__))
        # parent_path = path.parent.absolute()
    return path


@dataclasses.dataclass
class State:
    """ For storing the state of servers """
    state_changed: bool
    new_state: bool

    def __repr__(self):
        if self.state_changed:
            return f"State changed to {self.new_state}"
        else:
            return f"State unchanged, remains {self.new_state}"


class Server:
    """ Represents an individual server of a site """

    def __init__(self, name: str, ip: str, is_online: bool, status_cell: pyxl.Cell):
        self.name = name
        self.ip = ip
        self.is_online = is_online
        self.status_cell = status_cell

    def __repr__(self):
        return f"Server: {self.name}, {self.ip} [{'ONLINE' if self.is_online else 'OFFLINE'}]"


    def setState(self, state: State):
        self.is_online = state.new_state


class InvalidIPException(BaseException):
    pass
