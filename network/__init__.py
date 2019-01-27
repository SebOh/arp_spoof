import platform
from .network_commands import NetworkCommands


def is_windows():
    return platform == "win32"


def is_linux():
    return platform == "linux" or platform == "linux2"