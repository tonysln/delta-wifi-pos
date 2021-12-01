#!/usr/bin/env python

"""
app.py
Anton Slavin

Main application script.
Initialize the GUI and other components.
"""


# Packages
from PySide6.QtCore import Qt, QFile, QIODevice, QCoreApplication
from PySide6.QtWidgets import QApplication, QGraphicsScene
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtUiTools import QUiLoader
from scipy.interpolate import interp1d
import scanner
import locator
import sys


# Constants
UI_FILE_PATH = 'ui/app_main.ui'
ROUTERS_FILE_PATH = 'data/routers.csv'
LOCATIONS_FILE_PATH = 'data/locations.csv'


class MapRenderer(object):
    def __init__(self, window, routers, locations):
        self.window = window
        self.routers = routers # routers dictionary
        self.locations = locations # locations dictionary

        # Map details
        self.map_scale = 3
        self.img_w = 5300
        self.img_h = 5553

        # User location and router details
        self.user = {
            'x': 0, 
            'y': 0, 
            'floor': 1, 
            'location': 'Delta building',
            'precision': 0,
            'radius': 0
        }
        self.nearby_routers = []
        self.reset_labels()

    
    def scale_map(self):
        # Change map scaling
        pass

    
    def render(self):
        # Render the map
        print('Rendering...')

        # Load map for the current floor
        path = f'map/korrus-{self.user["floor"]}-c.png'
        # Init a pixmap for the map
        pix = QPixmap(path)
        painter = QPainter(pix)

        # Draw the user, routers and other information
        # ...

        painter.end()


        # Scale map based on current zoom
        scaled_w = self.window.mapView.width() * self.map_scale
        scaled_h = self.window.mapView.height() * self.map_scale
        pix = pix.scaled(scaled_w, scaled_h, 
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)

        # Add the pixmap to a scene in the QGraphicsView
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        self.window.mapView.setScene(scene)

        # Move the map to give padding around all sides
        self.window.mapView.setSceneRect(-100, -100, scene.width() + 200, scene.height() + 200)

        # Remap center coordinates based on the current map scale
        rc_x = interp1d([0, self.img_w], [0, scaled_w])
        rc_y = interp1d([0, self.img_h], [0, scaled_h])

        # Center map view on the user's location 
        self.window.mapView.centerOn(rc_x(self.user['x']), rc_y(self.user['y']))
        self.window.mapView.show()
        

    def draw_user(self):
        # Draw the user's location on map
        pass


    def draw_router(self):
        # Draw a router as a dot on map
        pass


    def highlight_router(self):
        # Highlight active routers
        pass


    def update_labels(self):
        # Write updated values to labels in sidebar menu
        # Only after the values have been loaded in
        self.window.coordsLabel.setText(f'x: {self.user["x"]}, y: {self.user["y"]}')
        self.window.floorLabel.setText(f'Floor {self.user["floor"]}')
        self.window.locationLabel.setText(self.user["location"])
        self.window.precLabel.setText(f'Precision: {self.user["precision"]} m')
        self.window.radiusLabel.setText(f'Radius: {self.user["radius"]} m')


    def reset_labels(self):
        # Reset map and all label values
        self.window.mapView.items().clear()
        self.window.scaleLabel.setText(str(self.map_scale))
        self.window.coordsLabel.setText('x: --, y: --')
        self.window.floorLabel.setText('Floor -')
        self.window.locationLabel.setText('---')
        self.window.precLabel.setText('Precision: -- m')
        self.window.radiusLabel.setText('Radius: -- m')



def begin_scan(renderer):
    print('Starting scanner & locator...')

    # Scan the network
    nearby = []
    # Predict a position
    user = {
            'x': 3800, 
            'y': 500, 
            'floor': 2, 
            'location': 'Delta building',
            'precision': 5,
            'radius': 2
        }

    # Pass data to renderer and draw
    renderer.nearby_routers = nearby
    renderer.user = user
    renderer.render()
    renderer.update_labels()



def load_routers(path):
    # Load data for all routers from storage

    # Open and read file
    with open(path, 'r') as f:
        rows = f.read().splitlines()

    # Skip first row
    if rows[0].startswith('mac'):
        rows = rows[1:]

    # Save router data into a dictionary
    routers_dict = {}
    for row in rows:
        row = row.split(',')

        # Ignore the last bit to speed up lookup
        # (1 entry for each router instead of 4)
        # TODO Needs more testing
        mac = row[0][:-1]
        routers_dict[mac] = {
            'x': int(row[1]),
            'y': int(row[2]),
            # 'floor': int(row[3]),
            # 'SSID': row[4],
            'freq': int(row[5])
        }

    return routers_dict


def load_locations(path):
    # Load data for all locations from storage

    # Open and read file
    with open(path, 'r') as f:
        rows = f.read().splitlines()

    # Skip first row
    if rows[0].startswith('mac'):
        rows = rows[1:]
    
    # Save locations into a dictionary with
    locations_dict = {}
    for row in rows:
        row = row.split(',')

        # Ignore last bit
        # TODO Needs more testing
        mac = row[0][:-1] 
        loc = row[1]
        locations_dict[mac] = loc

    return locations_dict


def load_UI(path):
    # Open UI file at given path
    ui_file = QFile(path)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f'Cannot open {path}: {ui_file.errorString()}')
        sys.exit(-1)

    # Load the UI into a window object
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)

    return window


if __name__ == "__main__":
    # Initial attributes
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    # Load window from UI file
    window = load_UI(UI_FILE_PATH)

    # Re-set window size
    window.setFixedSize(window.width(), window.height())

    # Load all routers and locations
    routers = load_routers(ROUTERS_FILE_PATH)
    locations = load_locations(LOCATIONS_FILE_PATH)

    # Init the main renderer class
    mr = MapRenderer(window, routers, locations)

    # Connect button controls
    window.quitButton.clicked.connect(sys.exit)
    window.scanButton.clicked.connect(lambda: begin_scan(mr))
    window.drawButton.clicked.connect(mr.render)
 
    # Display window and start app
    window.show()
    sys.exit(app.exec())
