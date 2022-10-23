import re

from downdetector.library.classes import Server
from downdetector.library.constants import INVALID

import ping3


def checkIfOnline(ip: str):
    # Sends one ping to the ip provided; returns true if the device replies, false if not.
    # Returns error types if they occur (OSError nad TypeError supported) or INVALID constant if ip is invalid.

    if validateIP(ip):
        return INVALID

    try:
        return bool(ping3.ping(dest_addr=ip))
    except OSError:
        return OSError
    except TypeError:
        return TypeError


def repeatedPing(ip: str, max_fails: int) -> bool:
    """
    Pings the ip provided, repeating max_fails times if it fails.
    :return: True if the device responds to one of the pings, otherwise False.
    """
    ping_count = 0
    while ping_count < max_fails:

        status = checkIfOnline(ip)

        if status == INVALID:
            ...
            # todo: notify of error (invalid ip)

        elif status == OSError:
            ...
            # todo: notify of error (likely disconnected)

        elif status == TypeError:
            ...
            # todo: notify of error (should never happen)

        # At this point status is either true (device online) or false (device offline)
        elif status:
            # Device online
            return True
        else:
            # Device offline
            ping_count += 1

    return False

#todo was checking this one when i left
def pingServers(servers: [Server], max_fails: int, failure_func=None, failure_args=tuple()):
    """
    Pings all the servers ips of all sites provided by the servers list. If a ping fails, it is pinged again until either
    it responds, or it fails max_fails times. Updates the online state of each server accordingly.

    :param servers: A list of AvigilonSite objects
    :param max_fails: The number of pings required for a server to be deemed offline
    :param failure_func: What is run when a site has an offline server
    :param failure_args: Arguments to be passed to failure_func when a server fails
    """

    # For each site
    for server in servers:
        # Ping all the server ips, keeping count of successes
        failure = False
        for ip in server.ips:
            # If this IP of the server is valid
            if validateIP(ip):
                # Ping; if a server fails, skip the rest of the site's IP addresses and break
                if not repeatedPing(ip, max_fails):
                    failure = True
                    break
            else:
                # Invalid IP
                failure = True
                break
                # todo: Notify of invalid IP address

        # Update server state
        server.all_online = not failure
        # todo test
        # Call the failure function if provided and supply it with the arguments
        if failure and failure_func:
            failure_func(*failure_args)


def validateIP(ip: str) -> bool:
    # Regex from https://devrescue.com/python-regex-for-ip-address/
    ip_regex = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    return bool(re.match(ip_regex, str(ip)))


if __name__ == "__main__":
    ...
    print(repeatedPing("192.168.1.1", 5))
    print(repeatedPing("192.168.1.0", 5))
    print(repeatedPing("", 5))
    print(repeatedPing("9+65+", 5))
    print(repeatedPing("192.5", 5))
    print(repeatedPing(None, 5))
