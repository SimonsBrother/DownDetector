""" Contains functions for reading data from the site spreadsheet """
import os

import openpyxl.worksheet.worksheet as pyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl import load_workbook

from downdetector.library.classes import Server
from downdetector.library.pinging import validateIP
# todo: IP validation

mac_excel_path = r"/Volumes/Public/Grade 3 Security Documents/BVH/BVH CCTV Support Checks/DownDetectorServers.xlsx"
windows_excel_path = r""

ONLINE = "ONLINE"
OFFLINE = "OFFLINE"


def getTestExcelPath():
    """ Returns the valid path for testing from within this python file """
    return windows_excel_path if os.name == "nt" else mac_excel_path


def validateSSPresence(path):
    """ Check the file exists """
    return os.path.isfile(path)


def getServerWorksheet(workbook: Workbook):
    """ Loads the worksheet from the Excel file from the path """
    return workbook["Servers"]


def getServers(worksheet: pyxl.Worksheet):
    """
    Gets all the servers from worksheet provided as a list of Server objects
    :param worksheet: The worksheet from the spreadsheet
    :return: A list of all the servers
    """

    site_name_buffer = ""
    server_list = []

    # For each row
    for row in worksheet.iter_rows(min_row=2, max_col=3):

        # Change the site name "buffer" if a new name is encountered
        if row[0].value is not None:
            site_name_buffer = str(row[0].value)

        # If an IP is available
        if row[1].value is not None:
            ip = str(row[1].value)

            status = str(row[2].value).lower()

            server_list.append(Server(site_name_buffer, ip, status == "online", row[2]))

    return server_list


def tweakWorksheet(path):
    """ Removes the statuses of blank rows, and sets any status that isn't 'Online' to 'Offline' """

    workbook = load_workbook(filename=path)
    worksheet = getServerWorksheet(workbook)
    # For each row
    for row in worksheet.iter_rows(min_row=2, max_col=3):

        # If there is an IP
        if row[1].value is not None:
            status = str(row[2].value)

            # Check if its status is valid
            if status not in (ONLINE, OFFLINE):
                # If invalid, set its state to OFFLINE
                setCellStatus(row[2], OFFLINE)
        else:
            setCellStatus(row[2], None)

    workbook.save(path)


def setCellStatus(cell: pyxl.Cell, status):
    """ Sets the status of a cell (for colouring later) """
    if status == ONLINE:
        cell.value = ONLINE

    elif status == OFFLINE:
        cell.value = OFFLINE

    elif status is None:
        cell.value = None

    else:
        raise ValueError("Invalid status")


if __name__ == "__main__":
    tweakWorksheet(getTestExcelPath())
    servers = getServers(getServerWorksheet(load_workbook(filename=getTestExcelPath())))
    for s in servers:
        print(s)
