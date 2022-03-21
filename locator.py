#!/usr/bin/env python

"""
locator.py
Anton Slavin

Script for performing positioning calculations.
"""


# Packages
import numpy as np
import math
import json


# Load constants from config
with open('config.json', 'r') as f:
    cfg = json.load(f)


def RSSI_to_dist(rssi):
    # Convert RSSI (signal strength) to distance in pixels.
    # https://stackoverflow.com/questions/62399361/swift-converting-rssi-to-distance
    # https://en.wikipedia.org/wiki/True-range_multilateration
    # https://en.wikipedia.org/wiki/Log-distance_path_loss_model
    # https://appelsiini.net/2017/trilateration-with-n-points/

    # Formula based on ...
    # Power stands for router power (max?)
    # Path loss is different for each environment and must be tweaked
    dist = 10 ** ((cfg['POWER'] - rssi)/(10 * cfg['PATH_LOSS']))
    return dist / cfg['PX_SCALE']


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
        router['DIST'] = dist / cfg['PX_SCALE'] # ?! TODO

        if dist < cfg['DIST_THRESHOLD']:
            near_coords.append((routers[mac]['x'], routers[mac]['y']))
            # Weight formula for the weighted mean method
            # TODO make heavier
            weight = 1 / router['RSSI']
            near_weights.append(weight)

            if dist > max_dist:
                max_dist = dist

    
    # -================== Trilateration ==================-
    if trilatOrMean:
        # Apply multilateration formulas to the formed circles
        # https://handwiki.org/wiki/Trilateration
        r1 = nearby_routers[0]['DIST']
        r2 = nearby_routers[1]['DIST']
        r3 = nearby_routers[2]['DIST']

        # Transform to cartestian coordinates for formula
        Ux,_ = scr_to_cart(near_coords[1][0], 0, cfg['IMG_W'], cfg['IMG_H'])
        Vx,Vy = scr_to_cart(near_coords[2][0], near_coords[2][1], cfg['IMG_W'], cfg['IMG_H'])
        x = (r1**2 - r2**2 + Ux**2) / (2*Ux)
        y = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*Vx*x) / (2*Vy)

        # Fix result by offsetting
        # TODO adjust vals dynamically
        xf = 1
        yf = 1
        sf = -1
        x += near_coords[xf][yf] * sf

        # Adjust back to screen coordinates
        x,y = cart_to_scr(x, y, cfg['IMG_W'], cfg['IMG_H'])



    # -================== Weighted Mean ==================-
    else:
        # Weighted average
        x,y = calc_w_avg_point(near_coords, near_weights)

        max_dist = 1.0
        for router in near_coords:
            rx,ry = router
            dist_to_mean = math.sqrt((rx - x)**2 + (ry - y)**2)

            if dist_to_mean > cfg['DIST_THRESHOLD']:
                print(dist_to_mean, router)

            # Custom dist precision for mean
            if dist_to_mean > max_dist:
                max_dist = dist_to_mean


    n = len(near_coords)
    # Precision is increased if more routers are nearby,
    # by 0.01 for each 10 additional routers
    coef = 0.05 - (math.ceil(n / 100) if n < 10 else math.floor(n / 10)) / 100
    user['precision'] = cfg['PX_SCALE'] * coef

    # Maximum radius is based on the maximum distance to a detected router
    user['radius'] = (max_dist / cfg['PX_SCALE']) * user['precision']

    # Clamp radius to avoid unrealistic values
    user['radius'] = min(user['radius'], cfg['RAD_THRESHOLD'])

    user['x'] = x
    user['y'] = y

    # Calculate the floor based on the mode floor
    user['floor'] = mode_floor(nearby_routers)

    # Return user object
    return user
