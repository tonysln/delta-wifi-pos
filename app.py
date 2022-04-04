#!/usr/bin/env python

"""
app.py
Anton Slavin

Main application script.
Initialize the GUI and other components.
"""


# Packages
from PySide6.QtCore import Qt, QFile, QIODevice, QCoreApplication, QPoint, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QApplication, QStatusBar
from PySide6.QtUiTools import QUiLoader
from scipy.interpolate import interp1d
import ui.components as uic
import scanner
import locator
import json
import sys



class MapRenderer(object):
    def __init__(self, window, routers, locations):
        self.window = window
        self.routers = routers # routers dictionary, mac[:]
        self.locations = locations # locations dictionary, mac[:-1]

        # Map details
        self.map_scale = 3
        self.img_w = cfg['IMG_W']
        self.img_h = cfg['IMG_H']

        # Font used to draw on map
        self.font = QFont('Arial', 38)

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
        self.add_new_router_mode = False
        self.new_router = {
            'x': 0,
            'y': 0,
            'floor': 1
        }

    
    def scale_map(self, up):
        # Change map scaling
        
        if not up and self.map_scale <= 4:
            self.map_scale += 1
        elif up and self.map_scale > 1:
            self.map_scale -= 1

        self.render()


    def change_displayed_floor(self, up):
        # Change the floor value to display a different floor

        if up and self.user['floor'] < 4:
            self.user['floor'] += 1
        elif not up and self.user['floor'] > 1:
            self.user['floor'] -= 1

        self.render()


    def remap_coords(self, reverse=False):
        # Remap coordinates based on the current map scale
        # Returns a tuple of interpolation functions for use
        # with x and y coordinates.
         
        scaled_w_range = [0, self.img_w / self.map_scale]
        scaled_h_range = [0, self.img_h / self.map_scale]
        img_w_range = [0, self.img_w]
        img_h_range = [0, self.img_h]
        
        # Map from scaled map to original map
        if reverse:
            rc_x = interp1d(scaled_w_range, img_w_range)
            rc_y = interp1d(scaled_h_range, img_h_range)
            return rc_x,rc_y

        # Map from original map to scaled map
        rc_x = interp1d(img_w_range, scaled_w_range)
        rc_y = interp1d(img_h_range, scaled_h_range)
        return rc_x,rc_y


    def render(self):
        # Render the map
        print('Rendering...')

        # Use a simple/clean or full map
        map_mode = '-c' if self.window.simpleMapView.isChecked() else ''
        # Load map for the current floor
        path = f'map/korrus-{self.user["floor"]}{map_mode}.png'
        # Init a pixmap for the map
        pix = QPixmap(path)
        painter = QPainter(pix)
        painter.setFont(self.font)

        # Highlight all detected routers
        for router in self.nearby_routers:
            self.highlight_router(painter, self.routers[router['MAC']])

        # Draw all routers on this floor
        for mac,router in self.routers.items():
            if router['floor'] == self.user['floor']:
                self.draw_router(painter, router)

                # Draw router location name on map
                painter.drawText(router['x'] - 40, router['y'] - 28, self.locations[mac[:-1]])

        self.draw_user(painter)

        # Init custom graphics scene
        scene = uic.CGraphicsScene()
        # Forward mouse click signals to update new router location info
        scene.signalMousePos.connect(lambda pos: self.add_router_on_click(pos))
        # If new router add mode is engaged, draw new router location
        if self.add_new_router_mode:
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.blue)
            center = QPoint(self.new_router["x"], self.new_router["y"])
            painter.drawEllipse(center, 22, 22)

        painter.end()


        # Scale map based on current zoom
        pix = pix.scaled(self.img_w / self.map_scale,
                         self.img_h / self.map_scale, 
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
        
        # Add the pixmap to a scene in the QGraphicsView
        scene.addPixmap(pix)
        self.window.mapView.setScene(scene)

        # Move the map to give padding around all sides
        self.window.mapView.setSceneRect(-100, -100, scene.width() + 200, scene.height() + 200)

        # Remap center coordinates based on the current map scale
        rc_x,rc_y = self.remap_coords()

        # Center map view on the user's location if not editing routers
        if not self.add_new_router_mode:
            center_x = rc_x(self.user['x'])
            center_y = rc_y(self.user['y'])
        else:
            # Otherwise, center on the new router
            center_x = rc_x(self.new_router['x'])
            center_y = rc_y(self.new_router['y'])
        
        self.window.mapView.centerOn(center_x, center_y)
        self.window.mapView.show()

        self.update_labels()
        # List all routers and their distances
        self.list_routers()


    def add_router_on_click(self, new_pos):
        # Handle clicks on map in case "add new router" mode is engaged

        if self.add_new_router_mode:
            rc_x,rc_y = self.remap_coords(reverse=True)
            self.new_router['x'] = int(rc_x(new_pos.x()).round())
            self.new_router['y'] = int(rc_y(new_pos.y()).round())
            self.new_router['floor'] = self.user['floor']
            self.nr.coords.setText(f'x: {self.new_router["x"]}, y: {self.new_router["y"]}')
            self.render()


    def draw_user(self, painter):
        # Draw the user's location on map
        
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QColor(0, 255, 40, 20))

        center = QPoint(self.user['x'], self.user['y'])
        rad = self.user['radius'] * cfg['PX_SCALE']

        # Outer circle
        painter.drawEllipse(center, rad, rad)

        # Inner circle/dot
        painter.setBrush(QColor(0, 255, 40, 180))
        painter.drawEllipse(center, 32, 32)


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
            mac = router['MAC']
            loc = self.locations[mac[:-1]]
            dist = router['DIST']
            # Formatted line
            rl +=  f'{loc}   ({round(dist, 1)} m)   {mac[-5:]}\n'

        self.window.routersListLabel.setText(rl)


    def update_labels(self):
        # Write updated values to labels in sidebar menu
        # Only after the values have been loaded in
        self.window.coordsLabel.setText(f'x: {round(self.user["x"])}, y: {round(self.user["y"])}')
        self.window.floorLabel.setText(f'Floor {self.user["floor"]}')
        self.window.locationLabel.setText(self.user["location"])
        self.window.precLabel.setText(f'Precision: {round(self.user["precision"], 2)} m')
        self.window.radiusLabel.setText(f'Radius: {round(self.user["radius"], 2)} m')


    def reset_labels(self):
        # Reset map and all label values
        self.window.mapView.items().clear()
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

    # Check if trilateration or mean method is selected
    trilatOrMean = renderer.window.trilatMethod.isChecked()

    # Scan the network
    nearby = [{'MAC': '7c:21:0d:2e:e5:20', 'RSSI': -57, 'SSID': 'eduroam'}, 
              {'MAC': '7c:21:0d:2e:e5:21', 'RSSI': -51, 'SSID': 'ut-public'}, 
              {'MAC': '7c:21:0d:2f:73:a0', 'RSSI': -68, 'SSID': 'eduroam'}, 
              {'MAC': '7c:21:0d:2f:75:21', 'RSSI': -81, 'SSID': 'ut-public'},
              {'MAC': '7c:21:0d:2f:75:20', 'RSSI': -77, 'SSID': 'eduroam'},
              {'MAC': '1c:d1:e0:44:97:e0', 'RSSI': -89, 'SSID': 'eduroam'}]
    
    if adapter:
        nearby = scanner.scan(adapter)

    if not nearby or len(nearby) == 0:
        window.status.showMessage('No nearby routers detected', 3000)
        return

    print('Nearby:')
    for item in nearby:
        print(item)

    print()

    # Filter out too weak and unknown routers
    print('Excluding:')
    for router in reversed(nearby):
        try:
            if router['RSSI'] < cfg['RSSI_MIN'] or router['MAC'] not in renderer.routers.keys():
                print(router)
                nearby.remove(router)
        except KeyError:
            window.status.showMessage('Malformed routers list', 3000)
            return
    
    print()

    # Predict user x, y, floor
    # NB! Nearby list gets mutated
    user = locator.locate(renderer.routers, nearby, trilatOrMean)

    # Set user location name based on nearest router
    user['location'] = renderer.locations[nearby[0]['MAC'][:-1]]

    # Pass data to renderer and draw
    renderer.nearby_routers = nearby
    renderer.user = user
    renderer.render()


def auto_scan(renderer, adapter=None):
    # Main Renderer object
    # Custom adapter name
    # Automatic scan (auto-update)

    activated = renderer.window.autoScanButton.isChecked()
    msg = 'Auto scan started' if activated else 'Auto scan stopped'
    window.status.showMessage(msg, 3000)

    if activated:
        # Do a scan
        begin_scan(renderer, adapter)
        # Repeat this method call in N seconds (will check if button still pressed too)
        QTimer.singleShot(cfg['AUTO_SEC']*1000, lambda: auto_scan(renderer, adapter))
        return


def load_routers(path):
    # Load data for all routers from storage

    # Open and read file
    with open(path, 'r') as f:
        rows = f.read().splitlines()

    # Skip first row
    if rows[0].startswith('x'):
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


def save_router(path, rr):
    # Save router (rr) entry
    
    router_str = f'\n{rr["x"]},{rr["y"]},{rr["MAC"]}' + \
                 f',{rr["SSID"]},{rr["floor"]},{rr["freq"]}'
    
    with open(path, 'a+') as f:
        f.write(router_str)


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


def save_location(path, router):
    # Save location entry

    location_str = f'\n{router["MAC"]},{router["name"]}'
    
    with open(path, 'a+') as f:
        f.write(location_str)


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


def add_new_router(renderer, nr_dialog):
    # Toggle add new router mode in renderer,
    # will enable mouse click capture on map

    renderer.add_new_router_mode = True
    renderer.render()
    nr_dialog.open()


def save_new_router(result_ok, renderer, nr_dialog):
    # Save new router details from the popup window and
    # save them to routers and locations data files
    
    data_ok, data = nr_dialog.get_fields(window)

    # User clicked on 'OK' and all fields are correct
    if result_ok and data_ok:
        # Check if a router with the same MAC already exists
        if data['MAC'] in renderer.routers.keys():
            window.status.showMessage('A router with the desired MAC already exists', 3000)
            add_new_router(renderer, nr_dialog)
            return


        data['x'] = renderer.new_router['x']
        data['y'] = renderer.new_router['y']
        data['floor'] = renderer.new_router['floor']

        # Save the new router entry
        save_router(cfg['ROUTERS_FILE_PATH'], data)
        save_location(cfg['LOCATIONS_FILE_PATH'], data)
        renderer.routers = load_routers(cfg['ROUTERS_FILE_PATH'])
        renderer.locations = load_locations(cfg['LOCATIONS_FILE_PATH'])

        # Reset labels and new router dict
        nr_dialog.reset()
        renderer.new_router = {'x': 0,'y': 0,'floor': 1}


    # User clicked on 'OK', but fields are not correct
    elif result_ok and not data_ok:
        add_new_router(renderer, nr_dialog)
        return

    # User clicked on 'Cancel', disable new router mode
    renderer.add_new_router_mode = False
    renderer.render()



if __name__ == "__main__":
    # Load config file
    with open('config.json', 'r') as f:
        cfg = json.load(f)

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
    window = load_UI(cfg['UI_FILE_PATH'])

    # Restrict window size
    window.setMinimumSize(window.width(), window.height())

    # Create a status bar
    window.status = QStatusBar()
    window.setStatusBar(window.status)

    # Load all routers and locations
    routers = load_routers(cfg['ROUTERS_FILE_PATH'])
    locations = load_locations(cfg['LOCATIONS_FILE_PATH'])

    # Init the main renderer class
    mr = MapRenderer(window, routers, locations)
    # Init new router dialog window
    nr_dialog = uic.NewRouterDialog()
    nr_dialog.finished.connect(lambda res: save_new_router(res, mr, nr_dialog))
    nr_dialog.floorUpButton.clicked.connect(lambda: mr.change_displayed_floor(True))
    nr_dialog.floorDownButton.clicked.connect(lambda: mr.change_displayed_floor(False))
    # Save new router dialog window object to the map renderer class
    mr.nr = nr_dialog

    # Connect button controls
    window.quitButton.clicked.connect(sys.exit)
    window.scanButton.clicked.connect(lambda: begin_scan(mr, adapter))
    window.autoScanButton.clicked.connect(lambda: auto_scan(mr, adapter))
    window.addNewRouterButton.clicked.connect(lambda: add_new_router(mr, nr_dialog))
    window.scalePlusButton.clicked.connect(lambda: mr.scale_map(True))
    window.scaleMinusButton.clicked.connect(lambda: mr.scale_map(False))
    window.simpleMapView.clicked.connect(lambda: mr.render())

    # Display window and start app
    window.status.showMessage('Ready', 3000)
    window.show()
    sys.exit(app.exec())
