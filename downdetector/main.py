import threading
import re

from downdetector.library.pinging import pingServers, pingCameras, validateIP
from downdetector.library.spreadsheet import getAvigilonSites, getTestExcelPath, getWorksheets

sites = getAvigilonSites(getWorksheets(getTestExcelPath()))

blacklisted = []


def pingingServers():
    pingServers(sites)


def listenForCommands():
    command = input("Input command: ")
    if command == "show blacklist":
        if len(blacklisted) != 0:
            print(f"The following IP addresses are blacklisted:")
            for ip in blacklisted:
                print(ip)
        else:
            print("No IP addresses are blacklisted.")

    elif command.startswith("blacklist "):
        ip = command.split(" ")[1]
        if validateIP(ip):
            blacklisted.append(ip)
            print(f"IP address {ip} is now blacklisted.")
        else:
            print("Invalid IP address.")

    else:
        print("Invalid command.")

    print()


while True:
    listenForCommands()
