#!/usr/bin/env python

"""
locator.py
Anton Slavin

Script for performing positioning calculations.
"""


# Packages
import numpy as np
import math


# Constants
DIST_THRESHOLD = 900.0
PX_SCALE = 11.0
POWER = 1.68
PATH_LOSS = 2.2


def RSSI_to_dist(rssi):
    # https://stackoverflow.com/questions/62399361/swift-converting-rssi-to-distance
    # https://en.wikipedia.org/wiki/True-range_multilateration
    # https://en.wikipedia.org/wiki/Log-distance_path_loss_model
    # https://appelsiini.net/2017/trilateration-with-n-points/

    dist = 10 ** ((POWER - rssi)/(10 * PATH_LOSS))

    # NB Mention in paper -> constants and variables very
    # important, need calibration and setup to ensure best
    # result with the type of building and layout.
    # More routers -> better, less routers -> tweak vars
    
    return dist / PX_SCALE


def calc_w_avg_point(locations, weights):
    # Calculate weighted average of given points

    try:
        centroid = np.average(locations, axis=0, weights=weights)
    except ZeroDivisionError:
        print("[!] Issue with weights:", weights)
        return 0, 0

    x, y = centroid[0], centroid[1]
    return x, y


def mode_floor(routers):
    # Calculate the mode of floor values

    all_floors = [int(rr['floor']) for rr in routers]
    freqs = {}
    # Count frequencies
    for item in all_floors:
        freqs[item] = all_floors.count(item)
    
    try:
        floor = max(freqs, key=freqs.get)
    except ValueError:
        print('[!] Unable to calculate floor from freqs:', all_floors)
        return 1

    return floor


def scr_to_cart(x, y, w, h):
    # Screen coordinates to cartesian
    cart_x = int(x) - int(w) // 2
    cart_y = -int(y) + int(h) // 2
    return cart_x,cart_y


def cart_to_scr(x, y, w, h):
    # Cartesian coordinates to screen
    scr_x = int(x) + (int(w) // 2)
    scr_y = -int(y) + (int(h) // 2)
    return scr_x,scr_y


def locate(routers, nearby_routers, trilatOrMean):
    # routers: dict of all routers
    # nearby_routers: list of nearby routers as dicts

    user = {}
    # Update nearby routers with the corresponding floor, 
    # coordinates, distance from RSSI
    near_coords = []
    near_weights = []   
    max_dist = 1.0
    for router in nearby_routers:
        mac = router['MAC']
        router['floor'] = routers[mac]['floor']
        
        # Distance from RSSI
        dist = RSSI_to_dist(router['RSSI'])
        router['DIST'] = dist / PX_SCALE # ?! TODO

        if dist < DIST_THRESHOLD:
            near_coords.append((routers[mac]['x'], routers[mac]['y']))
            weight = 1 / router['RSSI'] # TODO make heavier
            near_weights.append(weight)

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
        Ux,_ = scr_to_cart(near_coords[1][0], 0, 5300, 5553)
        Vx,Vy = scr_to_cart(near_coords[2][0], near_coords[2][1], 5300, 5553)
        x = (r1**2 - r2**2 + Ux**2) / (2*Ux)
        y = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*Vx*x) / (2*Vy)

        x -= near_coords[1][1] # ?! TODO
        x,y = cart_to_scr(x, y, 5300, 5553)
        
        user['precision'] = 20.0
        user['radius'] = user['precision']


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

        user['precision'] = (max_dist / PX_SCALE) * 0.5
        user['radius'] = user['precision']


    user['x'] = x
    user['y'] = y

    # Calculate the floor based on the mode floor
    user['floor'] = mode_floor(nearby_routers)

    # Return user object
    return user
