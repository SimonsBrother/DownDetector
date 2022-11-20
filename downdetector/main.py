from downdetector.library.pinging import getServerStatus
from downdetector.library.spreadsheet import getServers, tweakWorksheet, getTestExcelPath, setCellStatus, \
    getServerWorksheet, load_workbook, spreadsheetIsPresent

# todo BlockingIOError

# Get path
not_valid = True
path = input("Input the path to the spreadsheet (including the filename and extension, "
             "leave blank if the spreadsheet is empty)-\n>>>")
while not_valid:

    # Testing feature
    if path == "test":
        break

    not_valid = not spreadsheetIsPresent(path)
    if not_valid:
        path = input("Invalid path, try again: ")

# Get max fails
max_fails = input("Input how often to re-ping the servers (10 is recommended): ")
not_valid = True
while not_valid:
    # Ensure input is an integer
    try:
        max_fails = int(max_fails)
        not_valid = max_fails <= 0
        if not_valid:
            raise ValueError
    except ValueError:
        max_fails = input("Must be a whole number greater than 0: ")

# Get spreadsheet reload delay
reload_delay = input("Input the delay between spreadsheet reloads in hours: ")
not_valid = True
while not_valid:
    # Ensure input is an integer
    try:
        reload_delay = int(reload_delay)
        not_valid = reload_delay <= 0
        if not_valid:
            raise ValueError
    except ValueError:
        reload_delay = input("Must be a whole number greater than 0: ")

if path == "test":
    path = getTestExcelPath()

# Validate spreadsheet todo

# Automatic maintenance
tweakWorksheet(path)
# Get list of servers
servers = getServers(path)

input("Press enter")

while True:
    # For each server
    for server in servers:
        # Get server status
        status = getServerStatus(server, max_fails)

        # If the status has changed since last ping
        if status.state_changed:
            # Update the server object's state
            server.setState(status)

            # Update the server's status cell on the spreadsheet
            workbook = load_workbook(path)  # Load workbook
            worksheet = getServerWorksheet(workbook)  # Get worksheet
            setCellStatus(server.status_cell, status.new_state, worksheet)  # Set cell status
            workbook.save(path)  # Save
            workbook.close()  # then close the workbook

        print(server)
    break
