#!/usr/bin/env python

"""
scanner.py
Anton Slavin

Script for performing a live scan of nearby networks.
Supported on macOS, Windows and Linux distributions.

Main method is run(), which performs an OS platform check and launches
the appropriate method for scanning.

Returned data is in the form of a list of dict objects.
"""


# Packages
import subprocess as sp
import sys



def scan_macos():
    # Run the airport utility as a subprocess
    # NB! The utility must be enabled/linked beforehand
    res = sp.run(['airport', '-s'], capture_output=True)

    # Parse output from the airport scan
    networks = []
    result = res.stdout.decode().split('\n')
    for idx,row in enumerate(result):
        row = row.strip().split(' ')

        # Filter out first and invalid rows
        if idx == 0 or row[0] == '':
            continue

        # For now, do not include unknown networks
        if row[0] not in ['eduroam', 'ut-public']:
            continue

        # Check if any of the desired values are empty
        for i in range(0,3):
            if row[i] == '':
                print('[!] Incomplete data during nearby network parsing')
                print('Did you run the app as sudo?')
                quit(1)

        # First columns contain the required values
        # Based on the output of airport -s command
        network = {
            'SSID': row[0],
            'MAC': row[1],
            'RSSI': int(row[2])
        }
        networks.append(network)

    networks.sort(key=lambda x:x['RSSI'], reverse=True)
    return networks


def scan_linux(adapter):
    # TODO
    # Custom adapter name given as app argument
    if adapter:
        print(adapter)

    # possibly sudo airmon-ng start adapter
    # sudo airodump-ng !mon0! -> have to Ctrl-C
    # sudo airmon-ng stop adapter
    pass


def scan_win():
    # TODO
    # netsh wlan show all
    pass


def scan(adapter=None):
    # Launch the appropriate scanning method based on OS
    # Custom adapter name given for Linux, otherwise always None
    pf = sys.platform

    if pf == 'linux':
        return scan_linux(adapter)
    elif pf  == 'win32':
        return scan_win()
    elif pf == 'darwin':
        return scan_macos()
    else:
        print('[!] Unable to start a live scan')
        print('Your OS is not supported by this app.')
        sys.exit(1)
