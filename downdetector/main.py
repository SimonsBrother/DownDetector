from downdetector.library.pinging import getServerStatus
from downdetector.library.spreadsheet import getServers, tweakWorksheet, getTestExcelPath
from downdetector.library.classes import Server

path = getTestExcelPath()
max_fails = 10

tweakWorksheet(path)
servers = getServers(path)


print(getServerStatus(servers[0], 2))
exit()

while True:
    for server in servers:
        status = getServerStatus(server, max_fails)
        print(status)
