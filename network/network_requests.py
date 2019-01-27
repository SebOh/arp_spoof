from sys import platform
import re
import subprocess


class NetworkRequests:

    def __init__(self):
        pass

    def find_gateway(self):
        if _is_windows():
            return _find_gateway_windows()


def _find_gateway_windows():
            if _is_windows():
                ipconfig_result = subprocess.check_output(["ipconfig"])
                m = re.search("gateway[. ]*:\s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})", str(ipconfig_result))
                return m.group(1).strip()

            elif _is_linux():

                return ''


def _is_windows():
    return platform == "win32"


def _is_linux():
    return platform == "linux" or platform == "linux2"