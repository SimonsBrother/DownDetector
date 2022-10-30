import sys
from pathlib import Path
import os


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


class Server:
    """ Represents multiple avigilon servers on one site """

    def __init__(self, name: str, ip: str, server_type):
        self.name = name
        self.ip = ip
        self.is_online = True
        self.server_type = server_type

    def __repr__(self):
        ...  # todo


class InvalidIPException(BaseException):
    pass
