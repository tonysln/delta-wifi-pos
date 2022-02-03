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
    # https://en.wikipedia.org/wiki/Log-distance_path_loss_model
    # https://www.gaussianwaves.com/2013/09/log-distance-path-loss-or-log-normal-shadowing-model/
    # https://appelsiini.net/2017/trilateration-with-n-points/
    
    #pow(10, ((-56 -rssi)/(10*2)))*3.2808

    #N=2
    #power="1 meter RSSI"
    #10 ^ ((power – rssi)/(10 * N))

    #PL0 = txPower - RSSI
    #pow(10, ((double) (txPower - RSSI - PL0)) / (10 * 2))

    # NB limit to -70 at least, explain why
    # use categories/steps as in iBeaconing
    
    return 0.0



def locate(routers, nearby_routers):
    # routers: dict of all routers
    # nearby_routers: list of nearby routers as dicts

    # Return user object
    user = {
            'x': 500, 
            'y': 800, 
            'floor': 2,
            'precision': 5,
            'radius': 9
        }
    return user



def calc_dists(nearby_routers):
    # nearby_routers: list of nearby router as dicts
    # Add 'DIST' (in meters) for each router based on RSSI
    # NB In place!
    for router in nearby_routers:
        router['DIST'] = 12.56

