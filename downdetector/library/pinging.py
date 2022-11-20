import re

from downdetector.library.classes import Server, InvalidIPException, State

import ping3


def checkIfOnline(ip: str):
    """ Sends one ping to the ip provided; returns true if the device replies, false if not.
    May raise OSError, TypeError, InvalidError """

    if not validateIP(ip):
        raise InvalidIPException("IP address supplied is invalid.")

    return isinstance(ping3.ping(dest_addr=ip), float)


def repeatedPing(ip: str, max_fails: int) -> bool:
    """
    Pings the ip provided, repeating max_fails times if it fails.
    :return: True if the device responds to one of the pings, otherwise False.
    """
    ping_count = 0
    while ping_count < max_fails:

        status = checkIfOnline(ip)

        # At this point status is either true (device online) or false (device offline)
        if status:
            # Device online
            return True
        else:
            # Device offline
            ping_count += 1

    return False

# todo: test this thing
def getServerStatus(server: Server, max_fails: int) -> State:
    """
    Pings the server ip; if it doesn't reply, it is pinged until it responds, or it fails max_fails times.
    If it responds eventually, its online state is set to True, else it set to False
    :param server: The Server object to be pinged
    :param max_fails: The number of failed pings required for a server to be deemed offline
    :return: A tuple of 2 bools, with first element being whether a server changed state, second element being the new state
    """

    # Store previous online state of server
    prev_state = server.is_online
    # Ping server to get new state
    new_state = repeatedPing(server.ip, max_fails)

    # The state has changed if the new state is different
    state_changed = prev_state != new_state

    return State(state_changed, new_state)


def validateIP(ip: str) -> bool:
    # Regex from https://devrescue.com/python-regex-for-ip-address/
    ip_regex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    return bool(re.match(ip_regex, str(ip)))


if __name__ == "__main__":
    c = Server("My Mac", "192.168.1.28", False, None)
    print(c)

    while True:
        state = getServerStatus(c, 5)

        c.setState(state)
        if state.state_changed:
            ...
            print(state)

    exit()
    ...
    cases = [("192.168.1.1", 5),
             ("192.168.1.0", 5),
             ("", 5),
             ("9+65+", 5),
             ("192.5", 5),
             (None, 5)]

    for case in cases:
        try:
            print(repeatedPing(*case))
        except BaseException as e:
            print(e)
