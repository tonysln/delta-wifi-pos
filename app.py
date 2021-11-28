#!/usr/bin/env python

"""
app.py
Anton Slavin

Main application script.
Initialize the GUI and other components.
"""


# Packages
from PySide6.QtCore import Qt, QFile, QIODevice, QCoreApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
import sys


# Constants
UI_FILE_PATH = 'ui/app_main.ui'
ROUTERS_FILE_PATH = 'data/routers.csv'


class MapRenderer(object):
    def __init__(self, window, routers):
        self.window = window
        self.routers = routers

        # Map details
        self.map_scale = 4
        self.img_w = 5300
        self.img_h = 5553

        # User and router details
        self.user = None
        self.active_routers = []

        self.reset_labels()

    
    def reset_labels(self):
        # Reset map and all label values
        self.window.mapView.items().clear()
        self.window.scaleLabel.setText(str(self.map_scale))
        self.window.coordsLabel.setText('x: --, y: --')
        self.window.floorLabel.setText('Floor -')
        self.window.locationLabel.setText('---')
        self.window.precLabel.setText('Precision: -- m')
        self.window.radiusLabel.setText('Radius: -- m')

    
    def scale_map(self):
        # Change map scaling
        pass

    
    def render(self):
        # Render the map
        pass


    def draw_user(self):
        # Draw the user's location on map
        pass


    def draw_router(self):
        # Draw a router as a dot on map
        pass


    def highlight_router(self):
        # Highlight active routers
        pass



def load_routers(path):
    # Load data for all routers from storage
    return None


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

    # Load all routers
    routers = load_routers(ROUTERS_FILE_PATH)

    # Init the main renderer class
    mr = MapRenderer(window, routers)

    # Connect button controls
    window.quitButton.clicked.connect(sys.exit)
 
    # Display window and start app
    window.show()
    sys.exit(app.exec())
