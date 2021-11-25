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
 
    # Display window and start app
    window.show()
    sys.exit(app.exec())
