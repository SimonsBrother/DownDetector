""" Contains functions for reading data from the site spreadsheet """
import os

import openpyxl.worksheet.worksheet
from openpyxl import load_workbook

from downdetector.library.classes import AvigilonCamera, AvigilonSite
from downdetector.library.pinging import validateIP

# Constants
DEVICE_NAME = "Device Name"
IP_ADDRESS = "IP Address"
MAKE = "Make"
NIC_1 = "NIC 1"
SAMSUNG = "samsung"
HIKVISION = "hikvision"
AVIGILON = "avigilon"

mac_excel_path = "/Volumes/Public/Grade 3 Security Documents/Ballyvesey Misc/Site IP Devices/Site IP Devices.xlsx"
windows_excel_path = r"X:\Grade 3 Security Documents\Ballyvesey Misc\Site IP Devices\Site IP Devices.xlsx"


def validateSSPresence(path):
    return os.path.isfile(path)


def getWorksheets(path):
    """ Loads all the worksheets from the Excel file from the path """
    wb = load_workbook(filename=path)
    return wb.worksheets


def getCellPos(worksheet: openpyxl.worksheet.worksheet.Worksheet, contents: str):
    """ Gets the coordinates on a spreadsheet of a cell with the contents specified in the parameter """
    for row in worksheet.iter_rows():
        for cell in row:
            if str(cell.value) == contents:
                return cell.row, cell.column


def getAvigilonCameras(worksheet: openpyxl.worksheet.worksheet.Worksheet, server: AvigilonSite):
    """ Finds all the avigilon cameras associated with a server from the server's worksheet.
        Requires the related server object. """

    # Find the position of the Device Name header, since it is a unique header. Use it to find the camera headers position
    name_header_pos = getCellPos(worksheet, DEVICE_NAME)
    header_row = name_header_pos[0]

    # Use the Device Name header as an anchor to locate IP Address and Make headers
    make_header_pos = None
    ip_header_pos = None
    # Iterate through the header row, checking for IP Address and Make headers
    for cell in worksheet[header_row]:
        # Make header
        if cell.value == MAKE:
            make_header_pos = (cell.row, cell.column)
        # IP Address header
        elif cell.value == IP_ADDRESS:
            ip_header_pos = (cell.row, cell.column)

    # Check if the headers are not in position, raise an error if so
    if not (worksheet.cell(*name_header_pos).value == DEVICE_NAME and worksheet.cell(
            *make_header_pos).value == MAKE and worksheet.cell(*ip_header_pos).value == IP_ADDRESS):
        # Headers are not in position
        raise ValueError(
            f"Invalid header values.\nExpected: '{DEVICE_NAME}', got '{worksheet.cell(*name_header_pos).value}'"
            f"\nExpected: '{MAKE}', got '{worksheet.cell(*make_header_pos).value}'"
            f"\nExpected: '{IP_ADDRESS}', got '{worksheet.cell(*ip_header_pos).value}'")

    cameras = []
    # Iterate from row below header row to the bottom of the sheet (I'm assuming that there is nothing else under cameras)
    for i in range(header_row + 1, worksheet.max_row):
        # If the camera is avigilon
        if str(worksheet.cell(i, make_header_pos[1]).value).lower().strip(" ") == "avigilon":
            # Create new camera object
            cameras.append(AvigilonCamera(name=worksheet.cell(i, name_header_pos[1]).value,
                                          ip=worksheet.cell(i, ip_header_pos[1]).value,
                                          server=server))

    return cameras


def getAvigilonSites(worksheets: [openpyxl.worksheet.worksheet.Worksheet]):
    """ Finds all the avigilon servers and their cameras from the Site IP Devices spreadsheet. """

    sites = []
    for worksheet in worksheets:
        server_name = worksheet.title

        # Find the server Public IP header
        nic1_header_pos = getCellPos(worksheet, NIC_1)
        # Find the server header row
        server_header_row = nic1_header_pos[0]

        # Using the Public IP header as an anchor, find the Make header
        make_header_pos = None
        # Iterate through the header row, checking for the Make header
        for cell in worksheet[server_header_row]:
            if cell.value == MAKE:
                make_header_pos = (cell.row, cell.column)

        # Check if the Make is not in position, raise an error if so
        if worksheet.cell(*make_header_pos).value != MAKE:
            # Headers are not in position
            raise ValueError(
                f"Invalid header values, expected: '{MAKE}', got '{worksheet.cell(*make_header_pos).value}'")

        # Iterate from row below header row - until a blank cell is encountered in Make column, then break
        avigilon_ip_addresses = []
        for i in range(server_header_row + 1, worksheet.max_row):
            server_make_raw = worksheet.cell(i, make_header_pos[1]).value
            # If the end of the server rows have been reached, break
            if server_make_raw is None:
                break

            # If the server is not hikvision or samsung (and therefore it must be avigilon)
            server_make = str(server_make_raw).lower().strip(" ")
            if server_make != "hikvision" and server_make != "samsung":
                # Get the data from server's nic1 or whatever
                nic1_data = worksheet.cell(i, nic1_header_pos[1]).value
                if nic1_data is not None:
                    # Get the first region before a space; that is, the local IP address
                    ip_address = nic1_data.split(" ")[0]
                    if validateIP(ip_address):
                        # Append if valid
                        avigilon_ip_addresses.append(ip_address)

        if len(avigilon_ip_addresses) > 0:
            # The server object must be created first, so it can be assigned to the server's cameras
            server = AvigilonSite(name=server_name, ips=avigilon_ip_addresses, cameras=None)
            server.cameras = getAvigilonCameras(worksheet, server)  # Assign cameras
            sites.append(server)

    return sites


def getTestExcelPath():
    return windows_excel_path if os.name == "nt" else mac_excel_path


if __name__ == "__main__":
    servers_ = getAvigilonSites(getWorksheets(getTestExcelPath()))

    for s in servers_:
        print(s)
