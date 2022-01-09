#!/usr/bin/env python

"""
locator.py
Anton Slavin

Script for performing positioning calculations.
...
"""


# Packages
import math



def RSSI_to_dist(rssi):
    # https://stackoverflow.com/questions/62399361/swift-converting-rssi-to-distance
    # https://en.wikipedia.org/wiki/True-range_multilateration
    
    #pow(10, ((-56 -rssi)/(10*2)))*3.2808

    #N=2
    #power="1 meter RSSI"
    #10 ^ ((power – rssi)/(10 * N))

    #PL0 = txPower - RSSI
    #pow(10, ((double) (txPower - RSSI - PL0)) / (10 * 2))

    # NB limit to -70 at least, explain why
    # use categories/steps as in iBeaconing
    
    return 0.0


def locate(nearby_routers):
    return None
