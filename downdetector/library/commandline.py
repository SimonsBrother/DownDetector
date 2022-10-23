"""
Table of contents
------ Json control
--- Validate file presence
--- Load setting
--- Change setting
------ Blacklist commands
--- Add to blacklist
--- Delete from blacklist
--- Show blacklist contents [not a function]
------ Spreadsheet refresh
--- Show spreadsheet refresh
--- Change spreadsheet refresh
------ Info commands
--- Show offline servers and show offline cameras
------ Other
--- Shutdown todo
--- Processing commands
"""

import json

from downdetector.library.pinging import validateIP
from downdetector.library.constants import EXISTS, INVALID

example_json_data = {
    "spreadsheet_refresh_minutes": 120,
    "blacklisted": [],
    "offline_servers": [],
    "offline_cameras": []
}


# JSON control
def checkJSONPresence(path: str):
    """ Makes sure that the persistent data file exists """
    try:
        open(path, "r").close()
    except FileNotFoundError:
        with open(path, "w") as f:
            json.dump(example_json_data, f, indent=4)


def loadSetting(path: str, setting: str):
    """
    Gets information from the JSON file, assumes the file exists

    :param path: Path to persistent file
    :param setting: A key in the persistent folder, e.g., 'blacklisted'
    :return: The data of that setting
    """

    with open(path, "r") as f:
        return json.load(f)[setting]


def setSetting(path: str, setting: str, value):
    """
    Sets information from the JSON file, assumes the file exists

    :param path: Path to persistent file
    :param setting: A key in the persistent folder, e.g., 'blacklisted'
    :param value: The value to set the setting to
    """

    with open(path, "r") as f:
        data = json.load(f)

    with open(path, "w") as f:
        data[setting] = value
        json.dump(data, f, indent=4)


# Blacklist commands
def addToBlacklist(blacklist, ip):
    if validateIP(ip):
        if ip not in blacklist:
            blacklist.add(ip)
            # IP is valid and has been added to blacklist
            return True

        # IP already in blacklist
        return EXISTS

    # IP to add is not valid
    return INVALID


def deleteFromBlacklist(blacklist, ip):
    if ip in blacklist:
        blacklist.remove(ip)
        return True  # IP was deleted from blacklist

    return False  # IP is not in blacklist


# Spreadsheet refresh controls
def showSpreadsheetRefresh(path):
    return loadSetting(path, "spreadsheet_refresh_minutes")


def setSpreadsheetRefresh(path, value):
    setSetting(path, "spreadsheet_refresh_minutes", int(value))


# Info
# Works for both cameras and servers
def getOfflineDevices(devices):
    """
    Returns all the devices that are offline given a list of either AvigilonSite or AvigilonCamera objects

    :param devices: A list containing either AvigilonSite or AvigilonCamera objects
    :return: List of device object that are offline
    """
    offline_list = []

    # For each device
    for device in devices:
        try:
            # If the device is a server, this runs fine
            if not device.all_online:
                offline_list.append(device)

        except AttributeError:
            # The device must be a camera because of the AttributeError thrown
            if not device.online:
                offline_list.append(device)

    return offline_list


def processCommand(cmd: str, blacklist: set, path, sites):
    """
    ------ Blacklist commands
    --- Add to blacklist
    --- Delete from blacklist
    --- Show blacklist contents
    ------ Spreadsheet refresh
    --- Show spreadsheet refresh delay
    --- Change spreadsheet refresh delay
    ------ Info commands
    --- Show offline servers
    --- Show offline cameras
    ------ Other
    --- Shutdown todo
    """

    # Add to blacklist
    if cmd.startswith("blacklist"):
        try:
            ip = cmd.split(" ")[1]
        except IndexError:
            return "No IP address provided."

        response = addToBlacklist(blacklist, ip)
        if response == EXISTS:
            return f"IP address already added to blacklist."
        elif response == INVALID:
            return "Invalid IP address."
        else:
            return f"IP address {ip} added to blacklist."

    # Remove from blacklist
    elif cmd.startswith("unblacklist"):
        try:
            ip = cmd.split(" ")[1]
        except IndexError:
            return "No IP address provided."

        response = deleteFromBlacklist(blacklist, ip)
        if response:
            return f"IP address {ip} removed from blacklist."
        else:
            return f"IP address {ip} is not in the blacklist."

    # Show blacklist contents
    elif cmd == "show blacklist":
        if len(blacklist) == 0:
            return "Blacklist is empty."

        message = "Blacklist contains the following IP addresses:\n"
        for ip in blacklist:
            message += f"{ip}\n"
        return message

    # Show spreadsheet refresh delay
    elif cmd == "show ssrd":
        return f"The spreadsheet is updated every {showSpreadsheetRefresh(path)} minutes."

    # Change spreadsheet refresh delay
    elif cmd.startswith("set ssrd"):
        try:
            value = cmd.split(" ")[2]
        except IndexError:
            return "No value provided."

        try:
            if int(value) <= 0:
                return "Invalid value."
        except ValueError:
            return "Invalid value."

        setSpreadsheetRefresh(path, value)
        return f"Spreadsheet refresh delay has been set to {value} minutes."

    # Show offline servers
    elif cmd == "show offline servers":
        message = ""
        for offline_site in getOfflineDevices(sites):
            message += f"{offline_site.name}\n"

    # Show offline cameras
    elif cmd == "show offline cameras":
        message = ""

        for site in sites:
            # Get the offline cameras in each site
            offline_cams = getOfflineDevices(site.cameras)

            # If there are offline cameras:
            if len(offline_cams) > 0:
                # Display site name
                message += f"Site: {site.name}\n"
                # List offline cameras
                for offline_cam in offline_cams:
                    message += f"--- {offline_cam.name} (IP: {offline_cam.ip})\n"

                message += "\n"

        if message:
            return message
        else:
            return "No cameras are offline."

    # Shutdown
    elif cmd == "stop":
        return "Not yet implemented."

    else:
        return "Invalid command."


if __name__ == "__main__":
    blacklist_ = set()
    while True:
        print(processCommand(input("Input: "), blacklist_, "persistent.json"))
