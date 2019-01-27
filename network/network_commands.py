import network
import re
import subprocess


class NetworkCommands:

    def __init__(self):
        if network.is_windows():
            self.commands = NetworkCommandsWindows()
        pass

    def find_gateway(self):
        return self.commands.find_gateway()

    def set_ipv4_forwarding(self, enabled):
        return self.commands.set_ipv4_forwarding(enabled)


class NetworkCommandsWindows:

    def __init__(self):
        pass

    @staticmethod
    def find_gateway():
        """
        Finds the current default gateway ip based on the ipconfig command
        :return: gateway ip if possible. Else None
        """
        ipconfig_result = subprocess.check_output(["ipconfig"])
        m = re.search("gateway[. ]*:\s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})", str(ipconfig_result))
        if m:
            return m.group(1).strip()
        return None

    def set_ipv4_forwarding(self, enabled=True):
        """
        Enable or disable ipv4 forwarding on your machine. Root/admin right is required
        :param enabled: True or False
        :return: None
        """
        result = subprocess.check_output(["netsh", "interface", "ipv4", "show", "interfaces"])

        for (number, name) in re.findall("(\d{1,2})\s+(?:\d+)\s+(?:\d+)\s+connected\s([\w -.;]+)", str(result)):

            if self._ignore_interface(name):
                continue

            subprocess.check_output(
                ["netsh", "interface", "ipv4", "set",
                 "interface", number,
                 "forwarding=\"enabled\"" if enabled else "forwarding=\"disabled\""])

            print("[+]", "Enabled" if enabled else "Disabled", "IPv4 forwarding for", name.strip())

    @staticmethod
    def _ignore_interface(name):
        for i in ["Loopback Pseudo", "Npcap", "VirtualBox"]:
            if i in name:
                return True
        return False



