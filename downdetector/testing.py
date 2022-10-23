import downdetector.library.spreadsheet as spreadsheet
import downdetector.library.pinging as pinging

servers = spreadsheet.getAvigilonSites(spreadsheet.getWorksheets(spreadsheet.getTestExcelPath()))

if True:
    for server in servers:
        print(server)

    input("#" * 20)
    print("---")

    pinging.pingServers(servers, max_fails=1)

    for server in servers:
        print(server)

if True:
    i = 4
    for camera in servers[i].cameras:
        print(camera)

    input("#" * 20)
    print("---")

    pinging.pingCameras(servers[i].cameras, max_fails=1)

    for camera in servers[i].cameras:
        print(camera)
