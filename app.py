#!/usr/bin/env python

"""
app.py
Anton Slavin

Main application script.
Initialize the GUI and other components.
"""


# Packages
from PySide6.QtCore import Qt, QFile, QIODevice, QCoreApplication, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QApplication, QGraphicsScene
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
        self.routers = routers # routers dictionary, mac[:]
        self.locations = locations # locations dictionary, mac[:-1]

        # Map details
        self.map_scale = 3
        self.img_w = 5300
        self.img_h = 5553

        # Font used to draw on map
        self.font = QFont('', 32)

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

    
    def scale_map(self, up):
        # Change map scaling
        
        if up and self.map_scale <= 5:
            self.map_scale += 1
        elif not up and self.map_scale > 1:
            self.map_scale -= 1

        self.render()

    
    def render(self):
        # Render the map
        print('Rendering...')

        # Load map for the current floor
        path = f'map/korrus-{self.user["floor"]}-c.png'
        # Init a pixmap for the map
        pix = QPixmap(path)
        painter = QPainter(pix)
        painter.setFont(self.font)

        # Draw the user, routers and other information

        for router in self.nearby_routers:
            self.highlight_router(painter, self.routers[router['MAC']])

        for mac,router in self.routers.items():
            if router['floor'] == self.user['floor']:
                self.draw_router(painter, router)
                # Draw router location name on map
                painter.drawText(router['x'] - 38, router['y'] - 24, self.locations[mac[:-1]])

        self.draw_user(painter)

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

        self.update_labels()
        # List all routers and their distances
        self.list_routers()
        

    def draw_user(self, painter):
        # Draw the user's location on map
        
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QColor(0, 255, 40, 40))

        center = QPoint(self.user['x'], self.user['y'])
        rad = self.user['radius']

        # Outer circle
        painter.drawEllipse(center, rad, rad)

        # Inner circle/dot
        painter.setBrush(QColor(0, 255, 40, 200))
        painter.drawEllipse(center, 30, 30)


    def draw_router(self, painter, router):
        # Draw a router as a dot on map

        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(Qt.black)

        center = QPoint(router['x'], router['y'])
        painter.drawEllipse(center, 14, 14)


    def highlight_router(self, painter, router):
        # Highlight active routers
        
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(Qt.red)

        center = QPoint(router['x'], router['y'])
        painter.drawEllipse(center, 22, 22)


    def list_routers(self):
        # List all nearby routers and distances to them

        rl = ''
        for router in self.nearby_routers:
            loc = self.locations[router['MAC'][:-1]]
            # Shorten location name
            if len(loc) > 4:
                loc = loc[:4] + '. ' + loc[-4:]

            dist = router['DIST']
            rl +=  f'{loc}  ({round(dist, 1)} m)\n'

        self.window.routersListLabel.setText(rl)


    def update_labels(self):
        # Write updated values to labels in sidebar menu
        # Only after the values have been loaded in
        self.window.scaleLabel.setText(str(self.map_scale))
        self.window.coordsLabel.setText(f'x: {round(self.user["x"], 2)}, y: {round(self.user["y"], 2)}')
        self.window.floorLabel.setText(f'Floor {self.user["floor"]}')
        self.window.locationLabel.setText(self.user["location"])
        self.window.precLabel.setText(f'Precision: {round(self.user["precision"], 2)} m')
        self.window.radiusLabel.setText(f'Radius: {round(self.user["radius"] / 11.0, 2)} m')


    def reset_labels(self):
        # Reset map and all label values
        self.window.mapView.items().clear()
        self.window.scaleLabel.setText(str(self.map_scale))
        self.window.coordsLabel.setText('x: --, y: --')
        self.window.floorLabel.setText('Floor -')
        self.window.locationLabel.setText('---')
        self.window.precLabel.setText('Precision: -- m')
        self.window.radiusLabel.setText('Radius: -- m')
        self.window.routersListLabel.setText('')



def begin_scan(renderer, adapter=None):
    # Main Renderer object
    # Custom adapter name to use in Linux, otherwise
    # adapter name is None and default is used

    print('Starting scanner & locator...')

    # Scan the network
    # nearby = scanner.scan(adapter)
    # nearby = nearby[:3]
    # for item in nearby_test:
        # print(item)

    nearby = [{'MAC': '7c:21:0d:2e:e5:20', 'RSSI': -61, 'SSID': 'eduroam'}, 
              {'MAC': '7c:21:0d:2f:73:a0', 'RSSI': -64, 'SSID': 'eduroam'}, 
              {'MAC': '7c:21:0d:2f:75:21', 'RSSI': -81, 'SSID': 'ut-public'}]

    # Predict user x, y, floor
    # NB! nearby gets updated
    user = locator.locate(renderer.routers, nearby)

    # Set user location name based on nearest router
    user['location'] = renderer.locations[nearby[0]['MAC'][:-1]]

    # Pass data to renderer and draw
    renderer.nearby_routers = nearby
    renderer.user = user
    renderer.render()



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
        if len(row) == 0 or not row:
            continue

        row = row.split(',')

        mac = row[2]
        routers_dict[mac] = {
            'x': int(row[0]),
            'y': int(row[1]),
            'SSID': row[3],
            'floor': int(row[4]),
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
        if len(row) == 0 or not row:
            continue

        row = row.split(',')

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
    args = sys.argv
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(args)

    # Handle given arguments
    # Specified adapter to use (Linux only)
    adapter = None
    if '--adapter' in args:
        adapter = args[args.index('--adapter') + 1]


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
    window.scanButton.clicked.connect(lambda: begin_scan(mr, adapter))
    window.drawButton.clicked.connect(mr.render)

    window.scalePlusButton.clicked.connect(lambda: mr.scale_map(True))
    window.scaleMinusButton.clicked.connect(lambda: mr.scale_map(False))
 
    # Display window and start app
    window.show()
    sys.exit(app.exec())
