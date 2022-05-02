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
from scipy.interpolate import interp1d
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

        if not row[2].startswith('-'):
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

    return networks


def scan_linux(adapter):
    # Run the iw utility and parse output (despite being not recommended)
    # to get a list of nearby networks.
    # Custom adapter name given as app argument

    res = sp.run(['iw', adapter, 'scan'], capture_output=True)
    result = res.stdout.decode().split('\n')
    
    networks = []
    new_network = {}
    adding = False
    for row in result:
        row = row.strip().lower()

        if row.startswith('bss') and f'(on {adapter})' in row:
            if adding:
                networks.append(new_network)
                new_network = {}
            
            adding = True
            new_network['MAC'] = row[4:21]

        if adding and row.startswith('ssid:'):
            new_network['SSID'] = row[6:]

        if adding and row.startswith('signal:'):
            new_network['RSSI'] = int(row[8:11])

    networks.append(new_network)
    return networks


def scan_win():
    # Run the netsh utility and parse output to get a list
    # of nearby networks as detected by Wi-Fi adapter
    res = sp.run(['netsh', 'wlan', 'show', 'all'], capture_output=True)
    result = res.stdout.decode(encoding='cp1252').split('\n')

    networks = []
    new_network = {}
    display = False
    adding = False
    for row in result:
        if 'SHOW NETWORKS MODE=BSSID' in row:
            display = True

        if 'SHOW INTERFACE CAPABILITIES' in row:
            display = False

        if not display:
            continue

        row = row.strip().lower()
        if row.startswith('ssid '):
            if adding:
                networks.append(new_network)
                new_network = {}

            adding = True
            new_network['SSID'] = row.split(':')[1].strip()

        if adding and row.startswith('bssid'):
            new_network['MAC'] = row.split(':', 1)[1].strip()

        if adding and row.startswith('signal'):
            # Interpolate signal strength % to dBm
            conversion = interp1d([0, 100], [-100, -50])
            percent = int(row.split(':')[1].strip()[:-1])
            new_network['RSSI'] = conversion(percent)


    networks.append(new_network)
    return networks


def scan(adapter=None):
    # Launch the appropriate scanning method based on OS
    # Custom adapter name given for Linux, otherwise always None
    pf = sys.platform
    networks = []

    if pf == 'linux':
        networks = scan_linux(adapter)
    elif pf  == 'win32':
        networks = scan_win()
    elif pf == 'darwin':
        networks = scan_macos()
    else:
        print('[!] Unable to start a live scan')
        print('Your OS is not supported by this app.')
        sys.exit(1)

    # Try sorting networks if list not empty and not malformed
    try:
        networks.sort(key=lambda x:x['RSSI'], reverse=True)
    except KeyError as e:
        print('[!] Malformed list of networks, unable to find RSSI values.')
        return e

    return networks
