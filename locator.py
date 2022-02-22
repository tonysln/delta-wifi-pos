#!/usr/bin/env python

"""
locator.py
Anton Slavin

Script for performing positioning calculations.
"""


# Packages
import numpy as np
import math



def RSSI_to_dist(rssi):
    # https://stackoverflow.com/questions/62399361/swift-converting-rssi-to-distance
    # https://en.wikipedia.org/wiki/True-range_multilateration
    # https://en.wikipedia.org/wiki/Log-distance_path_loss_model
    # https://appelsiini.net/2017/trilateration-with-n-points/

    scale_px = 11.0
    power = 1.68 # NB Important -> Calibration
    N = 2.2
    dist = 10 ** ((power - rssi)/(10 * N)) / scale_px

    # NB Mention in paper -> constants and variables very
    # important, need calibration and setup to ensure best
    # result with the type of building and layout.
    # More routers -> better, less routers -> tweak vars
    
    return dist


def calc_w_avg_point(locations, weights):
    # Calculate weighted average of given points

    centroid = np.average(locations, axis=0, weights=weights)
    x, y, = centroid[0], centroid[1]
    return x, y


def mode_floor(routers):
    # Calculate the mode of floor values

    all_floors = [int(rr['floor']) for rr in routers]
    freqs = {}
    # Count frequencies
    for item in all_floors:
        freqs[item] = all_floors.count(item)
    
    floor = max(freqs, key=freqs.get)
    return floor


def locate(routers, nearby_routers, trilatOrMean):
    # routers: dict of all routers
    # nearby_routers: list of nearby routers as dicts

    DIST_THRESHOLD = 1200.0

    user = {}
    # Update nearby routers with the corresponding floor, 
    # coordinates, distance from RSSI, ...
    near_coords = []
    near_weights = []
    max_dist = 1.0
    for router in nearby_routers:
        mac = router['MAC']
        router['floor'] = routers[mac]['floor']
        
        # Distance from RSSI
        dist = RSSI_to_dist(router['RSSI'])
        router['DIST'] = dist / 11.0

        if dist < DIST_THRESHOLD:
            near_coords.append((routers[mac]['x'], routers[mac]['y']))
            near_weights.append(1 / router['RSSI'])

            # For trilat, temporary
            if dist > max_dist:
                max_dist = dist

    
    # -============ Trilateration ============-
    if trilatOrMean:
        # Apply multilateration formulas to the formed circles
        # https://handwiki.org/wiki/Trilateration
        r1 = nearby_routers[0]['DIST']
        r2 = nearby_routers[1]['DIST']
        r3 = nearby_routers[2]['DIST']
        Ux = near_coords[1][0]
        Vx = near_coords[2][0]
        Vy = near_coords[2][1]
        x = (r1**2 - r2**2 + Ux**2) / (2*Ux)
        y = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*Vx*x) / (2*Vy)
        # z = math.sqrt(r1**2 - x**2 - y**2)

        x += near_coords[0][0]
        
        user['precision'] = max_dist
        user['radius'] = max_dist


    # -============ Weighted Mean ============-
    else:
        # Weighted average
        x,y = calc_w_avg_point(near_coords, near_weights)

        max_dist = 1.0
        for router in near_coords:
            rx,ry = router
            dist_to_mean = math.sqrt((rx - x)**2 + (ry - y)**2)

            if dist_to_mean > DIST_THRESHOLD:
                print(dist_to_mean, router)

            # Custom dist precision for mean
            if dist_to_mean > max_dist:
                max_dist = dist_to_mean

        user['precision'] = max_dist / 2.0
        user['radius'] = max_dist / 2.0


    user['x'] = x
    user['y'] = y

    # Calculate the floor based on the mode floor
    user['floor'] = mode_floor(nearby_routers)

    # Return user object
    return user
