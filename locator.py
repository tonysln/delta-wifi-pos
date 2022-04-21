#!/usr/bin/env python

"""
locator.py
Anton Slavin

Script for performing positioning calculations.
"""


# Packages
from scipy.optimize import minimize
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

    dist_m = 10 ** ((cfg['POWER'] - rssi)/(10 * cfg['PATH_LOSS']))
    return dist_m / cfg['PX_SCALE']


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



# TODO temp, try out optimisation and MSE technique 
# from A. Zucconi's blog
def mse(x, locations, distances):
    # locations: [ (lat1, long1), ... ]
    # distances: [ distance1, ... ]
    # Source: https://www.alanzucconi.com/2017/03/13/positioning-and-trilateration/#part3
    mse = 0.0
    for location, distance in zip(locations, distances):
        distance_calculated = math.sqrt((x[0] - x[1])**2 + (location[0] - location[1])**2)
        mse += math.pow(distance_calculated - distance, 2.0)
    return mse / len(distances)

def loc_opt(initial_location, locations, distances):
    # initial_location: (lat, long)
    # locations: [ (lat1, long1), ... ]
    # distances: [ distance1,     ... ] 
    # Source: https://www.alanzucconi.com/2017/03/13/positioning-and-trilateration/#part3
    result = minimize(
                mse,
                initial_location,
                args=(locations, distances),
                method='L-BFGS-B',
                options={'ftol': 1e-5, 'maxiter': 1e+7}
            )
    location = result.x
    print(result)
    return location
# ===============================================


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
        router['DIST'] = dist / cfg['PX_SCALE']

        if dist < cfg['DIST_THRESHOLD']:
            near_coords.append((routers[mac]['x'], routers[mac]['y']))
            # Weight formula for the weighted mean method
            weight = 1 / router['RSSI']
            near_weights.append(weight)

            if dist > max_dist:
                max_dist = dist

    
    # -================== Trilateration ==================-
    if trilatOrMean:
        # Apply multilateration formulas to the formed circles

        r1 = nearby_routers[0]['DIST']
        r2 = nearby_routers[1]['DIST']
        r3 = nearby_routers[2]['DIST']

        botleft = sorted(near_coords, key=lambda x:x[0])[0]
        indices = {0, 1, 2}
        botleft_idx = near_coords.index(botleft)
        i1 = botleft_idx
        indices.remove(i1)
        i2 = indices.pop()
        i3 = indices.pop()

        # Transform to cartestian coordinates for formula
        # Using Fang's method where A = (0,0,0), B = (x2, 0, 0), C = (x3, y3, 0)
        Ux = near_coords[i2][0]
        Vx,Vy = near_coords[i3][0], near_coords[i3][1]
        x = (r1**2 - r2**2 + Ux**2) / (2*Ux)
        y = (r1**2 - r3**2 + Vx**2 + Vy**2 - 2*Vx*x) / (2*Vy)

        # Fix result by offsetting
        x += near_coords[i2][0]
        y += near_coords[i3][1]
        
        # Adjust back to screen coordinates
        # x,y = cart_to_scr(x, y, cfg['IMG_W'], cfg['IMG_H'])



    # -================== Weighted Mean ==================-
    else:
        # Weighted average
        x,y = calc_w_avg_point(near_coords, near_weights)

        max_dist = 1.0
        for router in near_coords:
            rx,ry = router
            dist_to_mean = math.sqrt((rx - x)**2 + (ry - y)**2)

            if dist_to_mean > cfg['DIST_THRESHOLD']:
                print("NB!!!", dist_to_mean, router)

            # Custom dist precision for mean
            if dist_to_mean > max_dist:
                max_dist = dist_to_mean


    n = len(near_coords)
    # Precision is increased if more routers are nearby,
    # by 0.01 for each 10 additional routers

    coef = cfg['RAD_NORM'] - (math.ceil(n / 100) if n < 10 else math.floor(n / 10)) / 100

    # Maximum radius is based on the maximum distance to a detected router
    user['radius'] = (max_dist / cfg['PX_SCALE']) * coef

    # Clamp radius to avoid unrealistic values
    user['radius'] = min(user['radius'], cfg['RAD_THRESHOLD'])

    user['x'] = x
    user['y'] = y

    # Calculate the floor based on the mode floor
    user['floor'] = mode_floor(nearby_routers)

    # Return user object
    return user
