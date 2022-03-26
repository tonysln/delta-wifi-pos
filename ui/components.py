from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QGraphicsScene, QLabel, QLineEdit, QRadioButton, QPushButton
from PySide6.QtCore import Qt, QPointF, Signal



class CGraphicsScene(QGraphicsScene):
    # Custom GraphicsScene class to capture the mouse
    # clicks for easily adding new routers.

    signalMousePos = Signal(QPointF)

    def __init__(self, parent=None):
        super(CGraphicsScene, self).__init__(parent)

    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        pos = QGraphicsSceneMouseEvent.lastScenePos()
        self.signalMousePos.emit(pos)



class NewRouterDialog(QDialog):
    # Custom dialog window for new router details.
    # Collects inserted data into a dictionary
    
    def __init__(self, parent=None):
        super(NewRouterDialog, self).__init__(parent)
        layout = QVBoxLayout(self)

        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle('New Router Details')
        self.setFixedSize(340, 280)

        # SSID
        self.ssidRow = QHBoxLayout()
        self.ssidRow.addWidget(QLabel('SSID'))
        self.ssidInputBox = QLineEdit()
        self.ssidInputBox.setFixedWidth(140)
        self.ssidRow.addWidget(self.ssidInputBox)
        layout.addLayout(self.ssidRow)

        # MAC
        self.macRow = QHBoxLayout()
        self.macRow.addWidget(QLabel('MAC'))
        self.macInputBox = QLineEdit()
        self.macInputBox.setFixedWidth(140)
        self.macRow.addWidget(self.macInputBox)
        layout.addLayout(self.macRow)

        # Location name
        self.nameRow = QHBoxLayout()
        self.nameRow.addWidget(QLabel('Name'))
        self.nameInputBox = QLineEdit()
        self.nameInputBox.setFixedWidth(140)
        self.nameRow.addWidget(self.nameInputBox)
        layout.addLayout(self.nameRow)

        # Frequency
        self.freqRow = QHBoxLayout()
        self.freqRow.addWidget(QLabel('Frequency'))
        self.freq2Choice = QRadioButton('2 GHz')
        self.freq2Choice.setChecked(True)
        self.freq5Choice = QRadioButton('5 GHz')
        self.freqRow.addWidget(self.freq2Choice)
        self.freqRow.addWidget(self.freq5Choice)
        layout.addLayout(self.freqRow)

        # Floor
        self.floorRow = QHBoxLayout()
        self.floorRow.addWidget(QLabel('Floor'))
        self.floorDownButton = QPushButton('<')
        self.floorDownButton.setFixedWidth(50)
        self.floorUpButton = QPushButton('>')
        self.floorUpButton.setFixedWidth(50)
        self.floorRow.addWidget(self.floorDownButton)
        self.floorRow.addWidget(self.floorUpButton)
        layout.addLayout(self.floorRow)

        # Coordinates
        self.coords = QLabel('x: 0, y: 0')
        layout.addWidget(self.coords)

        # OK and Cancel
        self.buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                        Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect buttons
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)


    def get_fields(self, window):
        # Collect text and choice from fields and radio buttons.
        # Returns a status boolean (all fields OK or not) and data

        data = {
            'SSID': self.ssidInputBox.text().strip(),
            'MAC': self.macInputBox.text().strip(),
            'name': self.nameInputBox.text().strip(),
            'freq': 2 if self.freq2Choice.isChecked() else 5
        }

        status_ok = True

        # Check inputs for missed fields
        if len(data['SSID']) == 0 or len(data['MAC']) == 0 or len(data['name']) == 0:
            window.status.showMessage('All new router fields must be filled in')
            status_ok = False

        if len(data['MAC']) != 17:
            window.status.showMessage('Malformed new router MAC address')
            status_ok = False

        return (status_ok,data)


    def reset(self):
        # Reset all fields

        self.ssidInputBox.setText('')
        self.macInputBox.setText('')
        self.nameInputBox.setText('')
        self.coords.setText('x: 0, y: 0')

