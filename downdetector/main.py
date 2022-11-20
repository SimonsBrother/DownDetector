from downdetector.library.pinging import getServerStatus
from downdetector.library.spreadsheet import getServers, tweakWorksheet, getTestExcelPath
from downdetector.library.classes import Server

path = getTestExcelPath()
max_fails = 1

tweakWorksheet(path)
servers = getServers(path)

input("Press enter")

while True:
    for server in servers:
        status = getServerStatus(server, max_fails)
        print(f"{server}, {status}")
    break
