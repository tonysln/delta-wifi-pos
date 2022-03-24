from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QGraphicsScene, QLabel, QLineEdit, QRadioButton
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

        # SSID
        self.ssidRow = QHBoxLayout()
        self.ssidRow.addWidget(QLabel('SSID'))
        ssidInputBox = QLineEdit()
        ssidInputBox.setFixedWidth(140)
        self.ssidRow.addWidget(ssidInputBox)
        layout.addLayout(self.ssidRow)

        # MAC
        self.macRow = QHBoxLayout()
        self.macRow.addWidget(QLabel('MAC'))
        macInputBox = QLineEdit()
        macInputBox.setFixedWidth(140)
        self.macRow.addWidget(macInputBox)
        layout.addLayout(self.macRow)

        # Location name
        self.nameRow = QHBoxLayout()
        self.nameRow.addWidget(QLabel('Name'))
        nameInputBox = QLineEdit()
        nameInputBox.setFixedWidth(140)
        self.nameRow.addWidget(nameInputBox)
        layout.addLayout(self.nameRow)

        # Frequency
        self.freqRow = QHBoxLayout()
        self.freqRow.addWidget(QLabel('Frequency'))
        freq2Choice = QRadioButton('2 GHz')
        freq5Choice = QRadioButton('5 GHz')
        self.freqRow.addWidget(freq2Choice)
        self.freqRow.addWidget(freq5Choice)
        layout.addLayout(self.freqRow)

        # OK and Cancel
        self.buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                        Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect buttons
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)


    def launch(self):
        res = self.open()
        # TODO connect to finished() 
        # TODO collect data from input boxes
        # TODO validate
        ok = res == QDialog.Accepted
        data = {}
        return (data, ok)
