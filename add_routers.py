#!/usr/bin/env python

"""
add_routers.py
Anton Slavin

Helper script for adding routers to a data file.
NB! This script applies to routers in the Delta building only.

During the data gathering phase it was discovered that every (?) router
in the Delta building broadcasts two networks: eduroam and ut-public, 
both in 2G and 5G frequencies, for a total of four networks.
All of these networks share the same MAC address except for the
least-significant bit, which is set as follows:

    0 - eduroam   2G
    f - eduroam   5G
    1 - ut-public 2G
    e - ut-public 5G

This script generates four entries (for each network) automatically,
only the coordinates, floor and a single MAC address are required.
"""


# Packages
import sys


# Constants
ROUTERS_FILE_PATH = 'data/routers.csv'


if __name__ == '__main__':
    args = sys.argv[1:]

    # Check if all args are present
    if len(args) != 4:
        print('[!] Usage:\n    python3 add_routers.py x y floor MAC')
        print('\nDelimiters in the MAC address are optional.')

    # Check if x, y and floor are numeric
    for arg in args[1:-1]:
        if not arg.isnumeric():
            print('[!] Argument is not numeric:', arg)
            quit(1)
    
    # Check if MAC has correct length
    if len(args[-1]) not in [12, 17]:
        print('[!] Incorrect MAC address format')
        quit(1)

    # Add delimiters to MAC if not present
    if len(args[-1]) == 12:
        mac = args[-1]
        args[-1] = ':'.join([mac[i:i+2] for i in range(0,12,2)])

    # Prepare values to write
    freqs = [2, 5, 2, 5]
    names = ['eduroam', 'eduroam', 'ut-public', 'ut-public']
    endings = ['0', 'f', '1', 'e']

    # Write values to file
    with open(ROUTERS_FILE_PATH, 'a') as f:
        for freq,name,end in zip(freqs, names, endings):
            mac = args[-1][:-1] + end # change MAC ending

            # Entry format: MAC,x,y,floor,SSID,frequency
            entry = f'{mac},{args[0]},{args[1]},{args[2]},{name},{freq}'

            f.write('\n')
            f.write(entry)
